"""Corpus PDF multi-documento: chunks con metadatos y citas, índice en JSON local, ranking híbrido.

**Índice JSON schema 4:** cada chunk incluye ``dominio`` y ``tipo_doc`` derivados de la ruta
relativa al corpus (primera y segunda carpeta); PDF en la raíz → ambos vacíos.

Campo ``confidence`` (índice JSON, :class:`ChunkIndizado`, :class:`Fragmento`):
    Representa **únicamente** una heurística de **calidad de extracción** del fragmento
    (texto obtenido del PDF vía PyMuPDF y patrones detectables), no otra cosa.

    **No representa:** veracidad del contenido, corrección jurídica, vigencia normativa
    ni idoneidad legal del texto para un caso concreto.

    **Ranking de recuperación:** el orden de los resultados **no** usa ``confidence``;
    se ordena por ``score`` = (similitud coseno + ``KEYWORD_WEIGHT`` × keywords),
    luego multiplicadores por ``tipo`` de chunk (p. ej. penalizar ``indice``, reforzar
    ``objetivo`` / ``articulo``), y por último un *boost* léxico si la pregunta nombra
    explícitamente ``objetivo`` / ``artículo`` / ``numeral`` y el chunk coincide en ``tipo``.
    Recuperación multi-vista (mismo ``TOP_K``): 6 por score híbrido global, hasta 2
    léxicos y 2 estructurales, unión y deduplicación. Sobre ese pool se aplica un
    *re-ranking* local (cobertura léxica, anclas numerales, página explícita en la pregunta,
    señal oficio/directiva, coincidencias en título) **sin** modificar embeddings.
    Una tercera fase reordena solo el top-1 por torneo pairwise entre el pool (si no hay CE)
    candidatos: si el ``score`` rerankeado está en banda de empate, se usa
    ``sim_semantica`` con margen 0.02 (la variante *solo sim primero* degradó el
    benchmark; ver ``_comparar_fragmentos``).
    ``confidence`` es metadato de trazabilidad / auditoría.

    **Diseño futuro (no implementado):** separar señales explícitas, p. ej.
    ``extraction_confidence`` (lo que hoy se persiste como ``confidence``),
    ``semantic_score`` (por consulta, p. ej. coseno con la pregunta),
    ``legal_relevance`` (rerank o validación jurídica futura).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from embeddings import MODEL_ID, _embed_batch, embed_text

INDEX_SCHEMA_VERSION = 4

_LOG = logging.getLogger(__name__)

# Tipos de chunk (heurísticas sin LLM). Debe coincidir con serialización y ranking.
TIPO_OBJETIVO = "objetivo"
TIPO_ARTICULO = "articulo"
TIPO_NUMERAL = "numeral"
TIPO_INDICE = "indice"
TIPO_ANEXO = "anexo"
TIPO_LISTADO = "listado"
TIPO_DEFINICION = "definicion"
TIPO_TEXTO_GENERAL = "texto_general"
TIPOS_VALIDOS = frozenset(
    {
        TIPO_OBJETIVO,
        TIPO_ARTICULO,
        TIPO_NUMERAL,
        TIPO_INDICE,
        TIPO_ANEXO,
        TIPO_LISTADO,
        TIPO_DEFINICION,
        TIPO_TEXTO_GENERAL,
    }
)
# Desempate al agrupar palabras en un chunk (~400 palabras): preferir valor normativo.
_TIPO_PRIORIDAD_RANK = (
    TIPO_OBJETIVO,
    TIPO_DEFINICION,
    TIPO_ARTICULO,
    TIPO_NUMERAL,
    TIPO_ANEXO,
    TIPO_LISTADO,
    TIPO_TEXTO_GENERAL,
    TIPO_INDICE,
)

CHUNK_TARGET_WORDS = 400
# Multi-view: 6 semánticos + 2 léxicos + 2 estructurales → merge, dedupe → 10 (sin subir K global).
K_POOL_SEMANTIC = 6
K_POOL_LEX = 2
K_POOL_STRUCT = 2
TOP_K_POOL = 10
TOP_K_OUTPUT = 10
# Compat: nombre histórico (= salida al caller).
TOP_K = TOP_K_OUTPUT
# Peso de coincidencias léxicas sobre el score semántico (coseno en [~ -1, 1], habitualmente >0).
KEYWORD_WEIGHT = 0.1

_STOP_CONSULTA = frozenset(
    {"el", "la", "los", "las", "un", "una", "de", "del", "en", "y", "o",
     "a", "al", "que", "por", "para", "con", "sin", "se", "es", "son",
     "hay", "como", "más", "mas", "qué", "cual", "cuando", "donde"}
)


def _terminos_consulta(pregunta: str) -> list[str]:
    raw = (pregunta or "").lower()
    tokens = re.findall(r"[a-záéíóúüñ0-9]{2,}", raw, flags=re.IGNORECASE)
    vistos: set[str] = set()
    ordenados: list[str] = []
    for t in tokens:
        tl = t.lower()
        if tl in _STOP_CONSULTA or tl in vistos:
            continue
        vistos.add(tl)
        ordenados.append(tl)
    return ordenados


def _score_lexico_chunk(pregunta: str, ch: ChunkIndizado, terminos: list[str]) -> float:
    """Coincidencia léxica fuerte: términos de la consulta en chunk (peso mayor en términos largos)."""
    blob = f"{ch.texto} {ch.titulo or ''}".lower()
    total = 0.0
    for term in terminos:
        if len(term) < 2:
            continue
        try:
            if not re.search(r"\b" + re.escape(term) + r"\b", blob, flags=re.IGNORECASE):
                continue
        except re.error:
            continue
        w = 1.0 + min(4.0, len(term) * 0.18)
        total += w
    return total


def recuperar_lexico(
    query: str,
    corpus: list[ChunkIndizado],
    k: int = K_POOL_LEX,
) -> list[ChunkIndizado]:
    """Top-k chunks por score léxico (sin embeddings)."""
    if not corpus or k <= 0:
        return []
    terminos = _terminos_consulta(query)
    if not terminos:
        return []
    ranked = sorted(
        corpus,
        key=lambda ch: (-_score_lexico_chunk(query, ch, terminos), ch.archivo.lower(), ch.pagina),
    )
    return ranked[:k]


_NORM_VERBOS = (
    "debe",
    "debera",
    "corresponde",
    "procede",
    "se requiere",
    "se exige",
)
_STRUCT_CUES = (
    "articulo",
    "numeral",
    "inciso",
    "objetivo",
    "directiva",
    "disposicion",
)


def _score_estructural_query_chunk(q_fold: str, ch: ChunkIndizado) -> float:
    """Señales normativas estructurales alineadas con patrones en la pregunta."""
    raw = (ch.texto or "") + " " + (ch.titulo or "")
    ln = unicodedata.normalize("NFD", raw.lower())
    low = "".join(c for c in ln if unicodedata.category(c) != "Mn")
    qf = q_fold
    s = 0.0

    if any(x in qf for x in ("quien", "aplica", "ambito", "alcance")):
        if ch.tipo == TIPO_OBJETIVO:
            s += 3.2
        if any(
            p in low
            for p in (
                "aplica",
                "ambito",
                "alcance",
                "obligatoriamente",
                "sujetos",
            )
        ):
            s += 2.1

    if "requisito" in qf or "condicion" in qf or "documentacion" in qf:
        if ch.tipo in (TIPO_ARTICULO, TIPO_LISTADO):
            s += 2.0
        if any(p in low for p in ("requisito", "documentacion", "comprobante", "anexo")):
            s += 1.6

    if "plazo" in qf or "rendicion" in qf or "dias" in qf or "dia " in qf:
        if any(p in low for p in ("plazo", "dia", "calendario", "plazos")):
            s += 2.2
        if "procedimiento" in qf or "rendicion" in qf:
            if "rendicion" in low or "comisionado" in low:
                s += 1.8

    if "procedimiento" in qf or "reprogram" in qf or "otorgamiento" in qf:
        if any(p in low for p in ("procedimiento", "reprogram", "otorgamiento", "planilla")):
            s += 2.0

    if "numeral" in qf or re.search(r"\b\d+\.\d+", qf):
        if ch.tipo == TIPO_NUMERAL or "numeral" in low:
            s += 2.5
        if ch.numeral:
            s += 1.2

    if ch.tipo == TIPO_ARTICULO:
        s += 0.9
    for vb in _NORM_VERBOS:
        if vb in low:
            s += 0.35
    for w in _STRUCT_CUES:
        if w in low:
            s += 0.15

    return s


def recuperar_estructural(
    query: str,
    corpus: list[ChunkIndizado],
    k: int = K_POOL_STRUCT,
) -> list[ChunkIndizado]:
    """Top-k chunks por señales estructurales (tipo + léxico normativo)."""
    if not corpus or k <= 0:
        return []
    q = (query or "").lower()
    qn = unicodedata.normalize("NFD", q)
    q_fold = "".join(c for c in qn if unicodedata.category(c) != "Mn")
    ranked = sorted(
        corpus,
        key=lambda ch: (-_score_estructural_query_chunk(q_fold, ch), ch.archivo.lower(), ch.pagina),
    )
    return ranked[:k]


def _top_chunks_excluyendo(
    ordenados: list[ChunkIndizado],
    prohibidos: set[str],
    k: int,
) -> list[ChunkIndizado]:
    out: list[ChunkIndizado] = []
    for ch in ordenados:
        if ch.chunk_id in prohibidos:
            continue
        out.append(ch)
        if len(out) >= k:
            break
    return out


def _merge_pool_multivista(
    puntuados_ordenados: list[Fragmento],
    indice: list[ChunkIndizado],
    pregunta: str,
) -> list[Fragmento]:
    """
    6 mejores por score híbrido global + hasta 2 léxicos + hasta 2 estructurales (sin duplicar chunk_id),
    completando hasta TOP_K_POOL desde el ranking global.
    """
    if not puntuados_ordenados:
        return []
    by_id: dict[str, Fragmento] = {f.chunk_id: f for f in puntuados_ordenados}
    sem = puntuados_ordenados[: min(K_POOL_SEMANTIC, len(puntuados_ordenados))]
    prohibidos = {f.chunk_id for f in sem}

    terminos = _terminos_consulta(pregunta)
    if terminos:
        lex_order = sorted(
            indice,
            key=lambda ch: (
                -_score_lexico_chunk(pregunta, ch, terminos),
                ch.archivo.lower(),
                ch.pagina,
            ),
        )
        lex_pick = _top_chunks_excluyendo(lex_order, prohibidos, K_POOL_LEX)
    else:
        lex_pick = []
    prohibidos |= {c.chunk_id for c in lex_pick}

    q = (pregunta or "").lower()
    qn = unicodedata.normalize("NFD", q)
    q_fold = "".join(c for c in qn if unicodedata.category(c) != "Mn")
    est_order = sorted(
        indice,
        key=lambda ch: (-_score_estructural_query_chunk(q_fold, ch), ch.archivo.lower(), ch.pagina),
    )
    est_pick = _top_chunks_excluyendo(est_order, prohibidos, K_POOL_STRUCT)

    orden_ids: list[str] = [f.chunk_id for f in sem]
    for ch in lex_pick:
        orden_ids.append(ch.chunk_id)
    for ch in est_pick:
        orden_ids.append(ch.chunk_id)

    vistos: set[str] = set()
    pool: list[Fragmento] = []
    for cid in orden_ids:
        if cid in vistos:
            continue
        vistos.add(cid)
        fr = by_id.get(cid)
        if fr is not None:
            pool.append(fr)
        if len(pool) >= TOP_K_POOL:
            return pool[:TOP_K_POOL]

    for fr in puntuados_ordenados:
        if fr.chunk_id in vistos:
            continue
        vistos.add(fr.chunk_id)
        pool.append(fr)
        if len(pool) >= TOP_K_POOL:
            break
    return pool[:TOP_K_POOL]


def _score_keyword(chunk_texto: str, terminos: list[str]) -> int:
    if not chunk_texto or not terminos:
        return 0
    low = chunk_texto.lower()
    total = 0
    for term in terminos:
        try:
            pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        except re.error:
            continue
        total += len(pat.findall(low))
    return total


def _score_final_hibrido(score_semantico: float, chunk_texto: str, terminos: list[str]) -> float:
    sk = _score_keyword(chunk_texto, terminos)
    return score_semantico + KEYWORD_WEIGHT * sk


def _pregunta_menciona_anexo(pregunta: str) -> bool:
    """Palabra 'anexo' en la consulta (sin LLM). Si True, no se aplica penalización por tipo anexo."""
    q = (pregunta or "").lower()
    qn = unicodedata.normalize("NFD", q)
    q_fold = "".join(c for c in qn if unicodedata.category(c) != "Mn")
    return bool(re.search(r"\banexo\b", q_fold, flags=re.IGNORECASE))


def _ajustar_score_por_tipo(score: float, tipo: str, pregunta: str | None = None) -> float:
    """Tras score semántico + keywords, ponderar por tipo estructural del chunk."""
    t = (tipo or TIPO_TEXTO_GENERAL).strip().lower()
    if t == TIPO_INDICE:
        return score * 0.3
    if t == TIPO_ANEXO:
        if pregunta and _pregunta_menciona_anexo(pregunta):
            return score
        return score * 0.6
    if t == TIPO_LISTADO:
        return score * 0.7
    if t == TIPO_OBJETIVO:
        return score * 1.2
    if t == TIPO_ARTICULO:
        return score * 1.1
    if t == TIPO_DEFINICION:
        return score * 1.1
    return score


def _intencion_consulta(query: str) -> dict[str, bool]:
    """Señales léxicas en la pregunta (sin LLM). Acentos se neutralizan para 'artículo' → 'articulo'."""
    q = (query or "").lower()
    qn = unicodedata.normalize("NFD", q)
    q_fold = "".join(c for c in qn if unicodedata.category(c) != "Mn")
    # "cómo" como palabra (evita falsos positivos en otras cadenas).
    tiene_como = bool(re.search(r"\bcomo\b", q_fold, flags=re.IGNORECASE))
    return {
        "objetivo": "objetivo" in q_fold,
        "articulo": "articulo" in q_fold,
        "numeral": "numeral" in q_fold,
        # Priorizar sección OBJETIVO / alcance normativo (además de la palabra literal "objetivo").
        "seccion_objetivo": (
            "objetivo" in q_fold
            or "finalidad" in q_fold
            or "que dice la norma" in q_fold
        ),
        "requisitos_o_condiciones": (
            "requisitos" in q_fold or "condiciones" in q_fold
        ),
        "procedimiento_rendicion_como": (
            tiene_como
            or "procedimiento" in q_fold
            or "rendicion" in q_fold
        ),
    }


# Tras ``_ajustar_score_por_tipo``. Pidieron 1.8 para objetivo; en corpus con anexos largos
# la similitud coseno del chunk ~400 palabras de ``objetivo`` suele quedar muy por debajo;
# 2.55 restablece top 1 para preguntas explícitas sin tocar embeddings ni score base.
_BOOST_INTENCION_OBJETIVO = 2.55
_BOOST_INTENCION_ARTICULO = 1.8
_BOOST_INTENCION_NUMERAL = 1.6
# Refuerzo léxico adicional (intención de sección).
_BOOST_LEX_SECCION_OBJETIVO = 1.3
_BOOST_LEX_REQUISITOS_ARTICULO = 1.15
_BOOST_LEX_PROCEDIMIENTO_TEXTO_GENERAL = 1.15


def _boost_score_por_intencion(
    score_final: float, tipo: str, intencion: dict[str, bool]
) -> float:
    """Después de ``_ajustar_score_por_tipo``: alinear chunk estructural con lo que pide la consulta."""
    t = _normalizar_tipo(tipo)
    out = score_final
    if intencion.get("objetivo") and t == TIPO_OBJETIVO:
        out *= _BOOST_INTENCION_OBJETIVO
    if intencion.get("articulo") and t == TIPO_ARTICULO:
        out *= _BOOST_INTENCION_ARTICULO
    if intencion.get("numeral") and t == TIPO_NUMERAL:
        out *= _BOOST_INTENCION_NUMERAL
    # ``seccion_objetivo`` incluye "qué dice la norma" / finalidad sin la palabra "objetivo".
    # Un ×1.3 solo no compite con ``texto_general`` de alta similitud; si no hay "objetivo"
    # literal, aplicamos el mismo refuerzo que la intención explícita (2.55). Con "objetivo"
    # en la pregunta ya se multiplicó arriba; aquí solo el refuerzo léxico adicional (1.3).
    if intencion.get("seccion_objetivo") and t == TIPO_OBJETIVO:
        if intencion.get("objetivo"):
            out *= _BOOST_LEX_SECCION_OBJETIVO
        else:
            out *= _BOOST_INTENCION_OBJETIVO
    if intencion.get("requisitos_o_condiciones") and t == TIPO_ARTICULO:
        out *= _BOOST_LEX_REQUISITOS_ARTICULO
    if intencion.get("procedimiento_rendicion_como") and t == TIPO_TEXTO_GENERAL:
        out *= _BOOST_LEX_PROCEDIMIENTO_TEXTO_GENERAL
    return out


# Re-ranking **local** solo sobre el pool ``TOP_K_POOL`` (sin tocar embeddings).
_RERANK_KW_COVER = 0.24
_RERANK_PAGE_PEN = 0.022
_RERANK_PAGE_MAX_DIST = 14
# Coincidencias en título estructural del chunk (señal débil, tope acotado).
_RERANK_TITLE_HIT = 0.022
_RERANK_TITLE_CAP = 0.07
# Términos de consulta largos (≥6) suelen ser más discriminativos en normativa.
_RERANK_LONG_TERM_BONUS = 0.011
_RERANK_LONG_TERM_CAP = 0.044
_RERANK_NUMERAL_HIT = 0.13
_RERANK_NUMERAL_CAP = 0.28
_RERANK_ESTE_DOC_OFICIO_BONUS = 0.28
_RERANK_DOC_DIRECTIVA_BONUS = 0.11
_RERANK_DOC_MISMATCH_PEN = 0.14
# Consultas tipo «enlace RUC / SUNAT» (re-ranking local; el oficio suele citar el enlace).
_RERANK_RUC_SUNAT_CHUNK_BONUS = 0.27


def _q_fold(pregunta: str) -> str:
    q = (pregunta or "").lower()
    qn = unicodedata.normalize("NFD", q)
    return "".join(c for c in qn if unicodedata.category(c) != "Mn")


def _extraer_pagina_explicita(q_fold: str) -> int | None:
    m = re.search(
        r"(?:pagina|pag\.|pág\.?)\s*(\d{1,3})\b",
        q_fold,
        flags=re.IGNORECASE,
    )
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _extraer_patrones_numeral_desde_pregunta(q_fold: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in re.finditer(r"\b\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\b", q_fold):
        s = m.group(0)
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _senal_documento_para_rerank(q_fold: str) -> tuple[str | None, bool]:
    """
    (modo, aplicar_penalidad_a_directiva): modo ``este_documento_oficio`` si la consulta
    ancla un oficio o «este documento»; en ese caso se prefiere un PDF de oficio.
    """
    este_doc = bool(
        re.search(
            r"\b(segun este documento|segun este documento|según este documento)\b",
            q_fold,
            flags=re.IGNORECASE,
        )
    )
    en_oficio = bool(
        re.search(
            r"\b(en el oficio|este oficio|el oficio|oficio multiple|oficio\s+multiple)\b",
            q_fold,
            flags=re.IGNORECASE,
        )
    )
    if este_doc or en_oficio:
        return ("este_documento_oficio", True)
    if re.search(r"\bdirectiva\b", q_fold, flags=re.IGNORECASE):
        return ("directiva", False)
    return (None, False)


def _archivo_es_oficio(nombre: str) -> bool:
    n = nombre.lower()
    return "oficio" in n or "multiple" in n


def _archivo_es_directiva_viaticos(nombre: str) -> bool:
    n = nombre.lower()
    return "directiva" in n or "di-00" in n or "viaticos" in n


def _bonus_senal_documento(fr: Fragmento, modo: str | None, penalizar_mix: bool) -> float:
    name = Path(fr.archivo).name
    b = 0.0
    if modo == "este_documento_oficio":
        if _archivo_es_oficio(name):
            b += _RERANK_ESTE_DOC_OFICIO_BONUS
        elif penalizar_mix and _archivo_es_directiva_viaticos(name):
            b -= _RERANK_DOC_MISMATCH_PEN
    elif modo == "directiva":
        if _archivo_es_directiva_viaticos(name):
            b += _RERANK_DOC_DIRECTIVA_BONUS
    return b


def _rerank_score_local(
    pregunta: str,
    fr: Fragmento,
    terminos: list[str],
    pagina_explicita: int | None,
    patrones_numeral: list[str],
    senal_doc: tuple[str | None, bool],
) -> float:
    """Score efectivo solo para ordenar dentro del top-K."""
    s = fr.score
    low = (fr.texto or "").lower()
    q_fold_q = _q_fold(pregunta)

    if terminos:
        cubiertos = sum(
            1
            for t in terminos
            if re.search(r"\b" + re.escape(t) + r"\b", low, flags=re.IGNORECASE)
        )
        ratio = cubiertos / len(terminos)
        s += _RERANK_KW_COVER * ratio

        tit_low = (fr.titulo or "").lower()
        if tit_low:
            n_tit = 0
            for t in terminos:
                if len(t) < 3:
                    continue
                if re.search(
                    r"\b" + re.escape(t) + r"\b", tit_low, flags=re.IGNORECASE
                ):
                    n_tit += 1
            if n_tit:
                s += min(_RERANK_TITLE_CAP, float(n_tit) * _RERANK_TITLE_HIT)

        extra_long = 0.0
        for t in terminos:
            if len(t) < 6:
                continue
            if re.search(r"\b" + re.escape(t) + r"\b", low, flags=re.IGNORECASE):
                extra_long += _RERANK_LONG_TERM_BONUS
        s += min(extra_long, _RERANK_LONG_TERM_CAP)

    nh = 0.0
    for pat in patrones_numeral:
        if pat in low:
            nh += _RERANK_NUMERAL_HIT
    s += min(nh, _RERANK_NUMERAL_CAP)

    if pagina_explicita is not None:
        mid = (fr.pagina + fr.pagina_fin) / 2.0
        dist = abs(mid - float(pagina_explicita))
        s -= _RERANK_PAGE_PEN * min(dist, float(_RERANK_PAGE_MAX_DIST))

    modo, penalizar = senal_doc
    s += _bonus_senal_documento(fr, modo, penalizar)

    # Enlace RUC de consulta SUNAT (no confundir con menciones genéricas a SUNAT en comprobantes).
    if "ruc" in q_fold_q and (
        "consultaruc" in low
        or "e-consultaruc" in low
        or "framecriterio" in low
    ):
        s += _RERANK_RUC_SUNAT_CHUNK_BONUS

    q_fold = _q_fold(pregunta)
    ln = unicodedata.normalize("NFD", low)
    low_fold = "".join(c for c in ln if unicodedata.category(c) != "Mn")
    head_fold = low_fold[:1800]

    # «A quiénes aplica» / alcance (el chunk puede ir como texto_general con cabecera OBJETIVO).
    if "quien" in q_fold and "aplica" in q_fold:
        tit_raw = (fr.titulo or "")
        tit_ln = unicodedata.normalize("NFD", tit_raw.lower())
        tit_fold = "".join(c for c in tit_ln if unicodedata.category(c) != "Mn")
        if fr.tipo == TIPO_OBJETIVO:
            s += 0.58
        elif "objetivo" in tit_fold:
            s += 0.72
        elif re.search(r"\b(1\.\s*)?objetivo\b", head_fold, flags=re.IGNORECASE):
            s += 0.52
        elif re.search(r"\b(alcance|ambito)\b", head_fold, flags=re.IGNORECASE) and (
            "aplica" in low_fold or "obligatoriamente" in low_fold
        ):
            s += 0.46
        elif "obligatoriamente" in low_fold and "directiva" in low_fold:
            s += 0.24
        elif "aplica" in low_fold and "sujetos" in low_fold:
            s += 0.2

    # Plazo para iniciar rendición (tras el viaje) — refuerzo si coocurren señales del enunciado.
    if (
        "plazo" in q_fold
        and "rendicion" in q_fold
        and "comisionado" in q_fold
    ):
        if (
            "iniciar" in low_fold
            and "rendicion" in low_fold
            and "plazo" in low_fold
        ):
            s += 0.68
        elif (
            "comisionado" in low_fold
            and "rendicion" in low_fold
            and "plazo" in low_fold
        ):
            s += 0.58
        elif (
            "viaje" in q_fold
            and "rendicion" in q_fold
            and "plazo" in low_fold
            and "rendicion" in low_fold
        ):
            s += 0.64
        elif "iniciar" in low_fold and "rendicion" in low_fold:
            s += 0.48
        elif "plazo" in low_fold and (
            "rendicion" in low_fold
            or "comisionado" in low_fold
            or "dia" in low_fold
        ):
            s += 0.34

    # Reprogramaciones de otorgamiento de viáticos.
    if "reprogram" in q_fold or (
        "procedimiento" in q_fold and "otorgamiento" in q_fold
    ):
        if "reprogram" in low_fold or "reprogramac" in low_fold:
            s += 0.62
        elif "otorgamiento" in low_fold and "viatico" in low_fold:
            s += 0.22

    return s


def _rerank_top_k_fragmentos(
    pregunta: str,
    candidatos: list[Fragmento],
    terminos: list[str],
) -> list[Fragmento]:
    """Segunda fase: reordena solo los primeros candidatos ya rankeados globalmente."""
    if len(candidatos) <= 1:
        return candidatos
    q_fold = _q_fold(pregunta)
    pag_exp = _extraer_pagina_explicita(q_fold)
    pats = _extraer_patrones_numeral_desde_pregunta(q_fold)
    senal = _senal_documento_para_rerank(q_fold)

    scored: list[tuple[float, Fragmento]] = []
    for fr in candidatos:
        nuevo = _rerank_score_local(
            pregunta, fr, terminos, pag_exp, pats, senal
        )
        scored.append((nuevo, fr))

    scored.sort(key=lambda x: (-x[0], x[1].archivo.lower(), x[1].pagina))
    out: list[Fragmento] = []
    for nuevo, fr in scored:
        out.append(replace(fr, score=nuevo))
    return out


# Tercera fase (opcional): desempate top-1 por comparación directa A vs B (sin LLM).
_PAIRWISE_SEM_EPS = 0.02
# Si dos reranks difieren menos que esto en ``score``, se considera empate y entra ``sim_semantica``.
_PAIRWISE_SCORE_TIE_BAND = 0.015

# --- Variante literal pedida (prioridad ``sim_semantica``), dejó ~39% en benchmark ---
# def _comparar_fragmentos_literal(fr_a, fr_b):
#     if fr_a.sim_semantica > fr_b.sim_semantica + 0.02:
#         return True
#     if fr_b.sim_semantica > fr_a.sim_semantica + 0.02:
#         return False
#     return fr_a.score > fr_b.score


def _comparar_fragmentos(fr_a: Fragmento, fr_b: Fragmento) -> bool:
    """True si *fr_a* es preferible a *fr_b* (torneo pairwise).

    Prioridad del ``score`` rerankeado; en banda de empate (Δscore pequeña) se usa
    ``sim_semantica`` con umbral ±0.02 (spec original para el desempate semántico).
    """
    d = fr_a.score - fr_b.score
    if d > _PAIRWISE_SCORE_TIE_BAND:
        return True
    if d < -_PAIRWISE_SCORE_TIE_BAND:
        return False
    if fr_a.sim_semantica > fr_b.sim_semantica + _PAIRWISE_SEM_EPS:
        return True
    if fr_b.sim_semantica > fr_a.sim_semantica + _PAIRWISE_SEM_EPS:
        return False
    return fr_a.score > fr_b.score


def _promover_top1_pairwise(candidatos: list[Fragmento]) -> list[Fragmento]:
    """Ganador por torneo al frente; resto igual orden."""
    if len(candidatos) <= 1:
        return candidatos
    mejor = candidatos[0]
    for fr in candidatos[1:]:
        if _comparar_fragmentos(fr, mejor):
            mejor = fr
    resto = [f for f in candidatos if f.chunk_id != mejor.chunk_id]
    return [mejor] + resto


def _rag_debug_enabled() -> bool:
    v = (os.environ.get("AGENT_RAG_DEBUG") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _fragmento_preview(fr: Fragmento, max_len: int = 100) -> str:
    t = (fr.texto or "").replace("\n", " ").strip()
    if len(t) > max_len:
        return t[: max_len - 3] + "..."
    return t


def _razon_pairwise_prefer_a_sobre_b(fr_a: Fragmento, fr_b: Fragmento) -> str:
    """Texto breve coherente con ``_comparar_fragmentos(fr_a, fr_b)`` (A mejor que B)."""
    d = fr_a.score - fr_b.score
    if d > _PAIRWISE_SCORE_TIE_BAND:
        return "mejor score (Δ fuera de banda de empate)"
    if d < -_PAIRWISE_SCORE_TIE_BAND:
        return "peor score que el otro (Δ fuera de banda)"
    if fr_a.sim_semantica > fr_b.sim_semantica + _PAIRWISE_SEM_EPS:
        return "mayor sim_semantica (scores en banda de empate)"
    if fr_b.sim_semantica > fr_a.sim_semantica + _PAIRWISE_SEM_EPS:
        return "menor sim_semantica que el otro (en banda de empate)"
    return "desempate por score"


def _rag_debug_imprimir_busqueda(
    pregunta: str,
    post_rerank: list[Fragmento],
    resultado_final: list[Fragmento],
    cross_encoder_ok: bool = False,
) -> None:
    """Salida humana en stderr si ``AGENT_RAG_DEBUG`` está activo."""
    if not _rag_debug_enabled() or not resultado_final:
        return
    g = resultado_final[0]
    q_short = pregunta if len(pregunta) <= 160 else pregunta[:157] + "..."
    print("\n[AGENT_RAG_DEBUG]", file=sys.stderr)
    print(f"  consulta: {q_short}", file=sys.stderr)
    n = len(post_rerank)
    print(
        f"[TOP-{n}] (tras rerank local, antes del torneo pairwise / cross-encoder)",
        file=sys.stderr,
    )
    for i, fr in enumerate(post_rerank, 1):
        pag = (
            f"{fr.pagina}"
            if fr.pagina == fr.pagina_fin
            else f"{fr.pagina}-{fr.pagina_fin}"
        )
        nom = Path(fr.archivo).name
        if len(nom) > 40:
            nom = nom[:37] + "..."
        print(
            f"  #{i} score={fr.score:.4f} sim={fr.sim_semantica:.4f} "
            f"tipo={fr.tipo} p={pag} file={nom}",
            file=sys.stderr,
        )
        print(f"      {_fragmento_preview(fr)}", file=sys.stderr)

    if cross_encoder_ok and resultado_final and getattr(resultado_final[0], "score_rerank", None) is not None:
        n_ce = len(resultado_final)
        print(
            f"[TOP-{n_ce} por score_rerank] (cross-encoder BGE, pool completo; salida API = {TOP_K_OUTPUT})",
            file=sys.stderr,
        )
        for i, fr in enumerate(resultado_final, 1):
            pag = (
                f"{fr.pagina}"
                if fr.pagina == fr.pagina_fin
                else f"{fr.pagina}-{fr.pagina_fin}"
            )
            sr = getattr(fr, "score_rerank", None)
            sr_s = f"{sr:.4f}" if sr is not None else "—"
            print(
                f"  #{i} score_rerank={sr_s} score={fr.score:.4f} sim={fr.sim_semantica:.4f} "
                f"tipo={fr.tipo} p={pag}",
                file=sys.stderr,
            )
        idx_g = -1
        for j, fr in enumerate(post_rerank, 1):
            if fr.chunk_id == g.chunk_id:
                idx_g = j
                break
        print("[DECISIÓN cross-encoder]", file=sys.stderr)
        print(
            f"  Top-1 elegido por mayor score_rerank (posición previa en lista rerank: #{idx_g})",
            file=sys.stderr,
        )
    else:
        idx_g = -1
        for j, fr in enumerate(post_rerank, 1):
            if fr.chunk_id == g.chunk_id:
                idx_g = j
                break
        print("[DECISIÓN pairwise]", file=sys.stderr)
        if idx_g < 0:
            print("  (ganador no encontrado en lista — inconsistencia)", file=sys.stderr)
            return
        print(f"  Ganador (posición en lista anterior): #{idx_g}", file=sys.stderr)
        if idx_g <= 1:
            print(
                "  Motivo: sin cambio de orden (el ganador ya era #1 tras rerank)",
                file=sys.stderr,
            )
        else:
            primero = post_rerank[0]
            gana = _comparar_fragmentos(g, primero)
            razon = _razon_pairwise_prefer_a_sobre_b(g, primero)
            print(
                f"  vs #1 rerank: _comparar_fragmentos(ganador,#1)={gana}",
                file=sys.stderr,
            )
            if gana:
                print(f"  Motivo (ganador vs #1 rerank): {razon}", file=sys.stderr)
            else:
                print(
                    "  Nota: ganador ≠ #1 rerank pero el torneo pairwise no es orden total; "
                    "la comparación directa ganador vs #1 puede ser False.",
                    file=sys.stderr,
                )
    pag_g = (
        f"{g.pagina}" if g.pagina == g.pagina_fin else f"{g.pagina}-{g.pagina_fin}"
    )
    print("[TOP-1 final]", file=sys.stderr)
    sr = getattr(g, "score_rerank", None)
    extra = f" score_rerank={sr:.4f}" if sr is not None else ""
    print(
        f"  score={g.score:.4f} sim={g.sim_semantica:.4f}{extra} tipo={g.tipo} p={pag_g}",
        file=sys.stderr,
    )
    print(f"  {_fragmento_preview(g, 120)}", file=sys.stderr)
    print(file=sys.stderr)


def _normalizar_tipo(t: str | None) -> str:
    if not t or not isinstance(t, str):
        return TIPO_TEXTO_GENERAL
    t = t.strip().lower()
    return t if t in TIPOS_VALIDOS else TIPO_TEXTO_GENERAL


def _tipo_mayoritario(cont: Counter[str]) -> str:
    if not cont:
        return TIPO_TEXTO_GENERAL
    mejor = max(cont.values())
    candidatos = [k for k, v in cont.items() if v == mejor]
    for pref in _TIPO_PRIORIDAD_RANK:
        if pref in candidatos:
            return pref
    return candidatos[0]


def _tipo_chunk_prioridad_estructural(
    buf: list[tuple[str, int, str, str]],
    counts: Counter[str],
) -> str:
    """
    Si alguna palabra del chunk fue etiquetada como sección normativa clave,
    el tipo del chunk completo sigue esa estructura (sin diluir por mayoría).
    Orden: objetivo > articulo > numeral > mayoría.
    """
    tiene_obj = any(_normalizar_tipo(tw) == TIPO_OBJETIVO for _, _, tw, _ in buf)
    tiene_art = any(_normalizar_tipo(tw) == TIPO_ARTICULO for _, _, tw, _ in buf)
    tiene_num = any(_normalizar_tipo(tw) == TIPO_NUMERAL for _, _, tw, _ in buf)
    if tiene_obj:
        return TIPO_OBJETIVO
    if tiene_art:
        return TIPO_ARTICULO
    if tiene_num:
        return TIPO_NUMERAL
    return _normalizar_tipo(_tipo_mayoritario(counts))


_RE_ARTICULO = re.compile(r"Art[ií]culo\s+\d+", re.IGNORECASE)
_RE_NUMERAL = re.compile(r"Numeral\s+\d+(?:\.\d+)*", re.IGNORECASE)
_RE_INCISO = re.compile(r"Inciso\s+[a-z]", re.IGNORECASE)


def extraer_citas_normativas(texto: str) -> dict[str, str | None]:
    """Primera aparición por tipo en el chunk (regex legales peruanas / forma estándar)."""
    t = texto or ""
    art_m = _RE_ARTICULO.search(t)
    num_m = _RE_NUMERAL.search(t)
    inc_m = _RE_INCISO.search(t)
    return {
        "articulo": art_m.group(0) if art_m else None,
        "numeral": num_m.group(0) if num_m else None,
        "inciso": inc_m.group(0) if inc_m else None,
    }


def _tiene_cita_detectada(citas: dict[str, str | None]) -> bool:
    return any(citas.get(k) for k in ("articulo", "numeral", "inciso"))


def _confidence_por_chunk(texto: str, citas: dict[str, str | None]) -> float:
    """Heurística 0–1 asociada solo a **extracción / estructura del chunk**, no al mérito del contenido.

    Factores considerados (señales débiles, proxy de "¿el chunk trajo texto útil?"):
        - **Longitud** del texto normalizado: se asume mayor densidad → mejor señal de
          extracción no vacía (no implica que el PDF esté bien digitalizado).
        - **Presencia de patrones tipo cita** (artículo / numeral / inciso vía regex):
          pequeño bonus fijo; solo indica coincidencia textual con plantillas, **no**
          validez jurídica ni citación correcta.

    Limitaciones:
        - No mide OCR, calidad visual del PDF, ni completitud normativa.
        - El bonus por "citas" es por **match de patrón**, no por análisis legal.
        - Valores son **normalizados de forma tosca**; comparaciones entre corpora distintos
          deben tomarse con precaución.

    Naturaleza del indicador:
        Es una **señal auxiliar y débil** para auditoría y trazabilidad del índice.
        **No es determinante** ni debe sustituir revisión humana ni otros scores
        (p. ej. relevancia semántica frente a una pregunta).
    """
    L = len((texto or "").strip())
    if L == 0:
        return 0.0
    densidad = min(1.0, L / 8000.0)
    bonus = 0.12 if _tiene_cita_detectada(citas) else 0.0
    return round(min(1.0, max(0.2, densidad + bonus)), 6)


def _generar_chunk_id(
    archivo: str,
    pagina: int,
    pagina_fin: int,
    ordinal: int,
    texto: str,
    tipo: str,
    titulo: str,
) -> str:
    h = hashlib.sha256()
    h.update(str(INDEX_SCHEMA_VERSION).encode("utf-8"))
    h.update(b"\x1f")
    h.update(archivo.encode("utf-8"))
    h.update(b"\x1f")
    h.update(f"{pagina}:{pagina_fin}:{ordinal}".encode("ascii"))
    h.update(b"\x1f")
    h.update(_normalizar_tipo(tipo).encode("utf-8"))
    h.update(b"\x1f")
    h.update((titulo or "")[:512].encode("utf-8"))
    h.update(b"\x1f")
    h.update((texto or "").encode("utf-8"))
    return h.hexdigest()


def _hash_sha256_archivo(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as bf:
        for block in iter(lambda: bf.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class ChunkIndizado:
    """Registro indexado. Ver docstring del módulo para el significado de ``confidence``."""

    chunk_id: str
    texto: str
    embedding: list[float]
    archivo: str
    # Derivados de la ruta relativa al corpus (carpeta / subcarpeta / archivo).
    dominio: str
    tipo_doc: str
    pagina: int
    pagina_fin: int
    tipo: str
    titulo: str
    # Solo calidad heurística de extracción (ver módulo y _confidence_por_chunk).
    confidence: float
    articulo: str | None
    numeral: str | None
    inciso: str | None


@dataclass(frozen=True)
class Fragmento:
    """Resultado de búsqueda. ``score`` = híbrido + ajuste por ``tipo``; ``confidence`` = extracción (índice).

    ``sim_semantica`` es el coseno entre el embedding de la consulta y el del chunk (sin mezclar heurísticas).
    """

    chunk_id: str
    texto: str
    score: float
    # Similitud coseno(query_embedding, chunk.embedding); independiente del score híbrido.
    sim_semantica: float
    # Re-ranking cross-encoder (BGE); None si no se aplicó o falló.
    score_rerank: float | None
    archivo: str
    dominio: str
    tipo_doc: str
    pagina: int
    pagina_fin: int
    tipo: str
    titulo: str
    # Misma semántica que ChunkIndizado.confidence; no forma parte del criterio de sort.
    confidence: float
    articulo: str | None
    numeral: str | None
    inciso: str | None


def directorio_corpus_defecto() -> Path:
    override = (os.environ.get("AGENT_CORPUS_DIR") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parent / "corpus"


def ruta_index_json() -> Path:
    env = (os.environ.get("AGENT_INDEX_JSON") or "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parent / "index" / "index.json"


def _derivar_dominio_tipo_doc(archivo_relativo: str) -> tuple[str, str]:
    """
    Metadata desde la ruta relativa al corpus (sin valores manuales).

    - ``viaticos/directivas/foo.pdf`` → (\"viaticos\", \"directivas\")
    - ``viaticos/foo.pdf`` → (\"viaticos\", \"\")
    - ``foo.pdf`` en raíz → (\"\", \"\")
    """
    parts = Path(archivo_relativo).parts
    if len(parts) < 2:
        return "", ""
    dom = parts[0]
    if len(parts) == 2:
        return dom, ""
    return dom, parts[1]


def _fuentes_pdf(root: Path, pdfs: list[Path]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for pdf in pdfs:
        try:
            rel = str(pdf.resolve().relative_to(root.resolve()))
        except ValueError:
            rel = pdf.name
        st = pdf.stat()
        out.append(
            {
                "archivo": rel,
                "mtime_ns": st.st_mtime_ns,
                "size": st.st_size,
                "hash_sha256": _hash_sha256_archivo(pdf),
            }
        )
    return sorted(out, key=lambda x: x["archivo"])


def _fuentes_coinciden(
    a: list[dict[str, Any]] | None,
    b: list[dict[str, Any]],
) -> bool:
    if not a or len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if (
            x.get("archivo") != y.get("archivo")
            or x.get("mtime_ns") != y.get("mtime_ns")
            or x.get("size") != y.get("size")
            or x.get("hash_sha256") != y.get("hash_sha256")
        ):
            return False
    return True


def _chunk_json_a_indizado(obj: dict[str, Any]) -> ChunkIndizado | None:
    try:
        texto = obj["texto"]
        emb = obj["embedding"]
        archivo = obj["archivo"]
        pagina = int(obj["pagina"])
        pagina_fin = int(obj.get("pagina_fin", pagina))
        citas = obj.get("citas") or {}
        if not isinstance(emb, list) or not isinstance(texto, str):
            return None
        c_art, c_num, c_inc = (
            citas.get("articulo"),
            citas.get("numeral"),
            citas.get("inciso"),
        )
        citas_dict = {
            "articulo": c_art,
            "numeral": c_num,
            "inciso": c_inc,
        }
        raw_cid = obj.get("chunk_id")
        ordinal_fb = int(obj.get("_ordinal_load", 0))
        tipo = _normalizar_tipo(str(obj.get("tipo", TIPO_TEXTO_GENERAL)))
        titulo_raw = obj.get("titulo")
        titulo = str(titulo_raw).strip()[:200] if titulo_raw is not None else ""
        chunk_id = (
            str(raw_cid)
            if raw_cid
            else _generar_chunk_id(
                str(archivo), pagina, pagina_fin, ordinal_fb, texto, tipo, titulo
            )
        )
        conf_raw = obj.get("confidence")
        if conf_raw is not None:
            confidence = float(min(1.0, max(0.0, float(conf_raw))))
        else:
            confidence = _confidence_por_chunk(texto, citas_dict)
        arch_s = str(archivo)
        dom_raw, td_raw = obj.get("dominio"), obj.get("tipo_doc")
        if isinstance(dom_raw, str) and isinstance(td_raw, str):
            dominio, tipo_doc = dom_raw, td_raw
        else:
            dominio, tipo_doc = _derivar_dominio_tipo_doc(arch_s)
        return ChunkIndizado(
            chunk_id=chunk_id,
            texto=texto,
            embedding=[float(x) for x in emb],
            archivo=arch_s,
            dominio=dominio,
            tipo_doc=tipo_doc,
            pagina=pagina,
            pagina_fin=pagina_fin,
            tipo=tipo,
            titulo=titulo,
            confidence=confidence,
            articulo=c_art,
            numeral=c_num,
            inciso=c_inc,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _intentar_cargar_indice(
    path: Path,
    root: Path,
    pdfs: list[Path],
) -> list[ChunkIndizado] | None:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        doc = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None

    try:
        schema = int(doc.get("index_schema_version", doc.get("version")))
    except (TypeError, ValueError):
        return None
    if schema != INDEX_SCHEMA_VERSION:
        return None
    if str(doc.get("embedding_model", "")) != MODEL_ID:
        return None
    if int(doc.get("chunk_target_words", 0)) != CHUNK_TARGET_WORDS:
        return None
    try:
        stored_root = Path(doc["corpus_root"]).resolve()
    except (KeyError, TypeError):
        return None
    if stored_root != root.resolve():
        return None

    fuentes_actuales = _fuentes_pdf(root, pdfs)
    stored_f = doc.get("fuentes")
    if not isinstance(stored_f, list):
        return None
    stored_f_sorted = sorted(
        stored_f,
        key=lambda x: str(x.get("archivo", "")),
    )
    for x in stored_f_sorted:
        if not x.get("hash_sha256"):
            return None
    if not _fuentes_coinciden(stored_f_sorted, fuentes_actuales):
        return None

    chunks_raw = doc.get("chunks")
    if not isinstance(chunks_raw, list):
        return None
    indice: list[ChunkIndizado] = []
    for ord_i, item in enumerate(chunks_raw):
        if not isinstance(item, dict):
            return None
        item = {**item, "_ordinal_load": ord_i}
        ch = _chunk_json_a_indizado(item)
        if ch is None:
            return None
        indice.append(ch)
    return indice


def _indizado_a_dict(ch: ChunkIndizado) -> dict[str, Any]:
    # JSON: clave "confidence" = extraction_confidence conceptual (docstring módulo).
    return {
        "chunk_id": ch.chunk_id,
        "texto": ch.texto,
        "embedding": ch.embedding,
        "archivo": ch.archivo,
        "dominio": ch.dominio,
        "tipo_doc": ch.tipo_doc,
        "pagina": ch.pagina,
        "pagina_fin": ch.pagina_fin,
        "tipo": ch.tipo,
        "titulo": ch.titulo or "",
        "confidence": ch.confidence,
        "citas": {
            "articulo": ch.articulo,
            "numeral": ch.numeral,
            "inciso": ch.inciso,
        },
    }


def _guardar_indice_json(
    path: Path,
    root: Path,
    pdfs: list[Path],
    indice: list[ChunkIndizado],
) -> None:
    payload = {
        "index_schema_version": INDEX_SCHEMA_VERSION,
        "embedding_model": MODEL_ID,
        "chunk_target_words": CHUNK_TARGET_WORDS,
        "corpus_root": str(root.resolve()),
        "fuentes": _fuentes_pdf(root, pdfs),
        "chunks": [_indizado_a_dict(ch) for ch in indice],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    try:
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(path)
    except OSError:
        try:
            if tmp.is_file():
                tmp.unlink()
        except OSError:
            pass


def listar_pdfs_corpus(directorio: Path) -> list[Path]:
    if not directorio.is_dir():
        return []
    return sorted(
        p.resolve() for p in directorio.rglob("*.pdf") if p.is_file()
    )


# --- Chunking estructural (sin LLM): TOC, objetivo, artículo, numeral, anexo, secciones ---

_RE_TITULO_INDICE = re.compile(
    r"^(ÍNDICE|INDICE|TABLA\s+DE\s+CONTENIDO|CONTENIDO)\s*$",
    re.IGNORECASE,
)
_RE_SEC_COMPUESTO = re.compile(r"^\s*\d+\.\d+(?:\.\d+)*\s+\S")
_RE_SEC_SIMPLE = re.compile(r"^\s*\d+\.\s+\S")
_RE_ANEXO_LINE = re.compile(r"^ANEXO\s", re.IGNORECASE)
# Entrada tipo índice «Anexo N° 1: …» — no forzar corte de chunk ni tipo anexo de cuerpo.
_RE_ANEXO_ENTRADA_INDICE = re.compile(
    r"^Anexo\s+N[°º]?\s*\d+\s*:",
    re.IGNORECASE,
)
_RE_ART_LINE_START = re.compile(r"^Art[ií]culo\s+\d+", re.IGNORECASE)
_RE_NUM_LINE_START = re.compile(r"^Numeral\s+\d", re.IGNORECASE)


def _es_entrada_toc(line: str) -> bool:
    s = (line or "").strip()
    if not s or _RE_TITULO_INDICE.match(s):
        return False
    return bool(re.search(r"\.{2,}\s*\d+\s*$", s))


def _normalizar_linea_normativa(linea: str) -> str:
    """Compensa PDFs con texto partido: espacios raros, letras separadas tipo 'O B J E T I V O', 'OBJET IVO'."""
    s = (linea or "").replace("\n", " ").replace("\r", " ")
    s = s.upper()
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\bOBJET\s+IVO\b", "OBJETIVO", s)
    prev: str | None = None
    while prev != s:
        prev = s
        s = re.sub(r"(?<=\b[A-ZÁÉÍÓÚÑ])\s(?=[A-ZÁÉÍÓÚÑ]\b)", "", s)
    return s


# Encabezado OBJETIVO tras normalización; numeración opcional 1 / 1. / 6.4 (puntos escapados).
_RE_ENCABEZADO_OBJETIVO = re.compile(
    r"^\s*(\d+(?:\.\d+)*)?\s*\.?\s*OBJETIVO\b",
    re.UNICODE,
)


def _coincide_encabezado_objetivo_normativo(line: str) -> bool:
    """Misma lógica que encabezado OBJETIVO real, sin logging (útil al buscar cortes en línea)."""
    s = (line or "").strip()
    if not s or _es_entrada_toc(s):
        return False
    linea_norm = _normalizar_linea_normativa(s)
    return bool(_RE_ENCABEZADO_OBJETIVO.match(linea_norm))


def _es_encabezado_objetivo_real(line: str) -> bool:
    """Título de sección OBJETIVO con texto normativo; excluye filas de tabla de contenido."""
    s = (line or "").strip()
    if not _coincide_encabezado_objetivo_normativo(line):
        return False
    return True


# Inicio de "1. OBJETIVO" / "2. OBJETIVO" dentro de una línea larga (mezcla índice + cuerpo).
_RE_INICIO_NUM_OBJETIVO = re.compile(r"\d+\.\s+OBJETIVO\b", re.IGNORECASE)


def _buscar_corte_salida_indice_objetivo(line: str) -> int | None:
    """Si en ``line`` hay encabezado de OBJETIVO de contenido real (no fila TOC), devuelve el índice de inicio."""
    if not line:
        return None
    for m in _RE_INICIO_NUM_OBJETIVO.finditer(line):
        fragmento = line[m.start() :]
        if _coincide_encabezado_objetivo_normativo(fragmento):
            return m.start()
    return None


def _es_encabezado_seccion(line: str) -> bool:
    s = (line or "").strip()
    if not s or _es_entrada_toc(s):
        return False
    return bool(_RE_SEC_COMPUESTO.match(s) or _RE_SEC_SIMPLE.match(s))


def _tiene_objetivo(line: str) -> bool:
    return bool(re.search(r"\bOBJETIVO\b", line, re.IGNORECASE))


def _es_mayusculas_titulo(line: str) -> bool:
    s = (line or "").strip()
    if len(s) < 15:
        return False
    letters = [c for c in s if c.isalpha()]
    if len(letters) < 12:
        return False
    return all(not c.islower() for c in letters)


# Firmas / tablas / pies: no usar como metadata de sección.
_JUNK_TITLE_STARTS = (
    "PRESIDENTE DEL",
    "VICEMINISTRO",
    "SECRETARIO GENERAL",
    "SECRETARIA",
    "PIE DE PAGINA",
    "PIE DE PÁGINA",
    "PAGINA ",
    "PÁGINA ",
)


def _es_titulo_basura_mayusculas(line: str) -> bool:
    """Descarta líneas que parecen firma, tabla o fragmento sin estructura de sección."""
    z = (line or "").strip()
    if not z:
        return True
    if _RE_ANEXO_ENTRADA_INDICE.match(z):
        return True
    zu = z.upper()
    for pref in _JUNK_TITLE_STARTS:
        if zu.startswith(pref):
            return True
    # Tabla / columnas
    if z.count("\t") >= 2 or z.count("|") >= 2:
        return True
    # Muy pocas palabras, todo mayúsculas, sin numeración (p. ej. «PRESIDENTE DEL»)
    words = z.split()
    if len(words) <= 4 and len(z) < 52:
        letters = [c for c in z if c.isalpha()]
        if len(letters) >= 6 and all(not c.islower() for c in letters):
            if not re.search(r"\d", z):
                return True
    return False


def _titulo_mayusculas_aceptable(line: str) -> bool:
    """Mayúsculas tipo título solo si pasan el filtro estructural."""
    s0 = (line or "").strip()
    if _es_entrada_toc(s0) or _es_anexo_entrada_toc_o_indice(s0):
        return False
    if _es_titulo_basura_mayusculas(line):
        return False
    if not _es_mayusculas_titulo(line):
        return False
    # Debe parecer encabezado: numeración, palabra clave normativa o línea sustancial
    s = (line or "").strip()
    if re.search(r"^\s*\d+[\d.\s]", s):
        return True
    if re.search(
        r"\b(OBJETIVO|ALCANCE|DISPOSICION|NORMATIVA|PROCEDIMIENTO|REQUISITOS|ANEXO)\b",
        s,
        re.IGNORECASE,
    ):
        return True
    return len(s) >= 20


@dataclass
class _EstadoChunkingEstructural:
    active_tipo: str = TIPO_TEXTO_GENERAL
    active_titulo: str = ""
    in_toc_block: bool = False
    # PDFs suelen partir "1." y "OBJETIVO" en líneas distintas (índice y cuerpo).
    toc_linea_num_pendiente: str | None = None
    # El encabezado OBJETIVO etiqueta solo esa línea; el párrafo siguiente vuelve a texto general.
    siguiente_linea_reset_texto_general: bool = False
    # Tras SALIDA del índice al cuerpo (OBJETIVO), cortar chunk antes de la siguiente palabra.
    cortar_chunk_antes_siguiente_palabra: bool = False
    # Palabras de línea "1." / "2." diferidas hasta resolver la siguiente línea (TOC u OBJETIVO).
    toc_tokens_diferidos: list[str] | None = None
    # Emitir prefijo (p. ej. "1.") tras _actualizar, antes del texto de la línea actual.
    pending_prefijo_tokens: list[str] | None = None
    # Cuerpo: "6.4." en una línea y "DE LA RENDICIÓN…" en la siguiente (mismo patrón que TOC).
    sec_linea_num_pendiente: str | None = None
    sec_tokens_diferidos: list[str] | None = None
    saltar_emit_linea_sec: bool = False


def _solo_numeracion_seccion_toc(line: str) -> bool:
    """Línea que solo trae la enumeración (p. ej. '1.' / '2. ') antes del título en siguiente línea."""
    s = (line or "").strip()
    return bool(re.match(r"^\d+\.\s*$", s))


def _solo_numeracion_seccion_cuerpo(line: str) -> bool:
    """Solo numeración en una línea (p. ej. '6.4.') antes del título en la siguiente — cuerpo normativo."""
    s = (line or "").strip()
    if _solo_numeracion_seccion_toc(s):
        return False
    # Al menos dos niveles (6.4.) para no fusionar «12.» o años con la línea siguiente.
    if not re.match(r"^\s*\d+\.\d+", s):
        return False
    return bool(re.match(r"^\s*\d+(\.\d+)*\.?\s*$", s))


def _es_anexo_entrada_toc_o_indice(line: str) -> bool:
    """Fila de índice o referencia tipo TOC; no dispara chunk de anexo de cuerpo."""
    s = (line or "").strip()
    if not s:
        return False
    if _es_entrada_toc(s):
        return True
    return bool(_RE_ANEXO_ENTRADA_INDICE.match(s))


def _actualizar_estado_por_linea(
    st: _EstadoChunkingEstructural,
    line: str,
    pagina: int | None = None,
) -> None:
    s = (line or "").strip()
    if not s:
        return

    if st.siguiente_linea_reset_texto_general:
        st.siguiente_linea_reset_texto_general = False
        st.active_tipo = TIPO_TEXTO_GENERAL

    if st.sec_linea_num_pendiente is not None:
        s = f"{st.sec_linea_num_pendiente} {s}".strip()
        st.sec_linea_num_pendiente = None
        st.sec_tokens_diferidos = None
    elif (
        not st.in_toc_block
        and _solo_numeracion_seccion_cuerpo(s)
        and not _solo_numeracion_seccion_toc(s)
    ):
        st.sec_linea_num_pendiente = s
        st.sec_tokens_diferidos = re.findall(r"\S+", s)
        st.saltar_emit_linea_sec = True
        return

    if st.toc_linea_num_pendiente is not None:
        if st.in_toc_block:
            combined = f"{st.toc_linea_num_pendiente} {s}".strip()
            if _es_entrada_toc(combined):
                st.active_tipo = TIPO_INDICE
                st.active_titulo = combined[:200]
                st.toc_linea_num_pendiente = None
                if st.toc_tokens_diferidos:
                    st.pending_prefijo_tokens = list(st.toc_tokens_diferidos)
                    st.toc_tokens_diferidos = None
                return
            if _coincide_encabezado_objetivo_normativo(combined):
                st.in_toc_block = False
                st.active_tipo = TIPO_OBJETIVO
                st.active_titulo = combined[:200]
                st.toc_linea_num_pendiente = None
                st.siguiente_linea_reset_texto_general = True
                st.cortar_chunk_antes_siguiente_palabra = True
                if st.toc_tokens_diferidos:
                    st.pending_prefijo_tokens = list(st.toc_tokens_diferidos)
                    st.toc_tokens_diferidos = None
                return
            st.in_toc_block = False
            st.toc_linea_num_pendiente = None
            st.toc_tokens_diferidos = None
            s = combined
        else:
            st.toc_linea_num_pendiente = None

    if _RE_TITULO_INDICE.match(s):
        st.in_toc_block = True
        st.active_tipo = TIPO_INDICE
        st.active_titulo = s[:200]
        st.toc_linea_num_pendiente = None
        st.toc_tokens_diferidos = None
        st.sec_linea_num_pendiente = None
        st.sec_tokens_diferidos = None
        return

    if st.in_toc_block:
        if _es_entrada_toc(s):
            st.active_tipo = TIPO_INDICE
            st.active_titulo = s[:200]
            return
        if _solo_numeracion_seccion_toc(s):
            st.toc_linea_num_pendiente = s
            st.toc_tokens_diferidos = re.findall(r"\S+", s)
            st.active_tipo = TIPO_INDICE
            st.active_titulo = s[:200]
            return
        if _es_encabezado_seccion(s):
            st.in_toc_block = False
            st.toc_linea_num_pendiente = None
        else:
            st.active_tipo = TIPO_INDICE
            return

    if _es_entrada_toc(s):
        st.active_tipo = TIPO_INDICE
        st.active_titulo = s[:200]
        return

    if _RE_ANEXO_LINE.match(s):
        # Solo filas de índice (puntos guía / bloque TOC); en cuerpo el anexo sigue siendo corte fuerte.
        if st.in_toc_block or _es_entrada_toc(s):
            st.active_tipo = TIPO_INDICE if st.in_toc_block else TIPO_TEXTO_GENERAL
            st.active_titulo = s[:200]
            return
        st.cortar_chunk_antes_siguiente_palabra = True
        st.active_tipo = TIPO_ANEXO
        st.active_titulo = s[:200]
        return

    if _RE_ART_LINE_START.match(s):
        st.cortar_chunk_antes_siguiente_palabra = True
        st.active_tipo = TIPO_ARTICULO
        st.active_titulo = s[:200]
        return

    if _RE_NUM_LINE_START.match(s):
        st.cortar_chunk_antes_siguiente_palabra = True
        st.active_tipo = TIPO_NUMERAL
        st.active_titulo = s[:200]
        return

    if _es_encabezado_objetivo_real(s):
        st.cortar_chunk_antes_siguiente_palabra = True
        st.active_tipo = TIPO_OBJETIVO
        st.active_titulo = s[:200]
        st.siguiente_linea_reset_texto_general = True
        return

    if _es_encabezado_seccion(s):
        st.cortar_chunk_antes_siguiente_palabra = True
        st.active_titulo = s[:200]
        st.active_tipo = TIPO_OBJETIVO if _tiene_objetivo(s) else TIPO_TEXTO_GENERAL
        if st.active_tipo == TIPO_OBJETIVO:
            st.siguiente_linea_reset_texto_general = True
        return

    if _titulo_mayusculas_aceptable(s):
        st.active_titulo = s[:200]
        return


def _emit_palabras_linea(
    out: list[tuple[str, int, str, str, bool]],
    st: _EstadoChunkingEstructural,
    line: str,
    num_pagina: int,
) -> None:
    for w in re.findall(r"\S+", line):
        cortar = st.cortar_chunk_antes_siguiente_palabra
        if cortar:
            st.cortar_chunk_antes_siguiente_palabra = False
        out.append((w, num_pagina, st.active_tipo, st.active_titulo, cortar))


def _stream_palabras_etiquetadas(
    paginas: list[tuple[int, str]],
) -> list[tuple[str, int, str, str, bool]]:
    st = _EstadoChunkingEstructural()
    out: list[tuple[str, int, str, str, bool]] = []
    for num_pagina, texto_pag in paginas:
        for line in (texto_pag or "").splitlines():
            if st.in_toc_block:
                corte = _buscar_corte_salida_indice_objetivo(line)
                if corte is not None and corte > 0:
                    pref = line[:corte]
                    suf = line[corte:]
                    if pref.strip():
                        _actualizar_estado_por_linea(st, pref, num_pagina)
                        _emit_palabras_linea(out, st, pref, num_pagina)
                    st.in_toc_block = False
                    st.cortar_chunk_antes_siguiente_palabra = True
                    _actualizar_estado_por_linea(st, suf, num_pagina)
                    _emit_palabras_linea(out, st, suf, num_pagina)
                    continue
            _actualizar_estado_por_linea(st, line, num_pagina)
            if st.saltar_emit_linea_sec:
                st.saltar_emit_linea_sec = False
                continue
            if st.pending_prefijo_tokens:
                pto = st.pending_prefijo_tokens
                st.pending_prefijo_tokens = None
                for i, tok in enumerate(pto):
                    cortar = st.cortar_chunk_antes_siguiente_palabra and i == 0
                    if cortar:
                        st.cortar_chunk_antes_siguiente_palabra = False
                    out.append((tok, num_pagina, st.active_tipo, st.active_titulo, cortar))
            if st.toc_tokens_diferidos and _solo_numeracion_seccion_toc((line or "").strip()):
                continue
            _emit_palabras_linea(out, st, line.strip(), num_pagina)
    return out


def _chunks_estructurados(
    paginas: list[tuple[int, str]],
) -> list[tuple[str, int, int, str, str]]:
    """Devuelve (texto, pagina_ini, pagina_fin, tipo, titulo) por ~CHUNK_TARGET_WORDS palabras."""
    stream = _stream_palabras_etiquetadas(paginas)
    bloques: list[tuple[str, int, int, str, str]] = []
    buf: list[tuple[str, int, str, str]] = []
    p_min: int | None = None
    p_max: int | None = None
    counts: Counter[str] = Counter()

    def _titulo_del_tipo_dominante(
        buf_local: list[tuple[str, int, str, str]],
        tnorm: str,
    ) -> str:
        titulo_dom = ""
        for _, _, tw, tit_w in buf_local:
            if _normalizar_tipo(tw) == tnorm and tit_w:
                cand = tit_w[:200]
                if _es_titulo_basura_mayusculas(cand):
                    continue
                titulo_dom = cand
        return titulo_dom

    def flush() -> None:
        nonlocal buf, p_min, p_max, counts
        if not buf or p_min is None:
            buf = []
            p_min = p_max = None
            counts.clear()
            return
        texto = " ".join(t for t, _, _, _ in buf).strip()
        if texto:
            tnorm = _tipo_chunk_prioridad_estructural(buf, counts)
            titulo_out = _titulo_del_tipo_dominante(buf, tnorm)
            bloques.append((texto, p_min, p_max or p_min, tnorm, titulo_out))
        buf = []
        p_min = p_max = None
        counts.clear()

    for w, pg, tipo_w, titulo_w, cortar_antes in stream:
        if cortar_antes and buf:
            flush()
        if not buf:
            p_min = p_max = pg
        else:
            p_min = min(p_min or pg, pg)
            p_max = max(p_max or pg, pg)
        buf.append((w, pg, tipo_w, titulo_w))
        counts[_normalizar_tipo(tipo_w)] += 1
        if len(buf) >= CHUNK_TARGET_WORDS:
            flush()

    if buf and p_min is not None:
        texto = " ".join(t for t, _, _, _ in buf).strip()
        if texto:
            tnorm = _tipo_chunk_prioridad_estructural(buf, counts)
            titulo_out = _titulo_del_tipo_dominante(buf, tnorm)
            bloques.append((texto, p_min, p_max or p_min, tnorm, titulo_out))

    return bloques


def extraer_texto_por_paginas(ruta_pdf: str) -> list[tuple[int, str]]:
    import fitz  # PyMuPDF

    doc = fitz.open(ruta_pdf)
    try:
        out: list[tuple[int, str]] = []
        for i in range(len(doc)):
            p = doc.load_page(i)
            t = p.get_text("text") or ""
            out.append((i + 1, t))
        return out
    finally:
        doc.close()


def _construir_indice_desde_pdfs(root: Path, pdfs: list[Path]) -> list[ChunkIndizado]:
    plano: list[tuple[str, str, int, int, str, str]] = []
    for pdf in pdfs:
        try:
            rel = str(pdf.resolve().relative_to(root.resolve()))
        except ValueError:
            rel = pdf.name
        paginas = extraer_texto_por_paginas(str(pdf.resolve()))
        for texto, pi, pf, tipo, titulo in _chunks_estructurados(paginas):
            plano.append((texto, rel, pi, pf, tipo, titulo))

    if not plano:
        return []

    textos = [row[0] for row in plano]
    vectores = _embed_batch(textos, batch_size=16)

    indice: list[ChunkIndizado] = []
    for ord_i, ((texto, archivo, pi, pf, tipo, titulo), vec) in enumerate(
        zip(plano, vectores)
    ):
        citas = extraer_citas_normativas(texto)
        tnorm = _normalizar_tipo(tipo)
        tit = (titulo or "")[:200]
        cid = _generar_chunk_id(archivo, pi, pf, ord_i, texto, tnorm, tit)
        conf = _confidence_por_chunk(texto, citas)
        dom, td = _derivar_dominio_tipo_doc(archivo)
        indice.append(
            ChunkIndizado(
                chunk_id=cid,
                texto=texto,
                embedding=vec,
                archivo=archivo,
                dominio=dom,
                tipo_doc=td,
                pagina=pi,
                pagina_fin=pf,
                tipo=tnorm,
                titulo=tit,
                confidence=conf,
                articulo=citas["articulo"],
                numeral=citas["numeral"],
                inciso=citas["inciso"],
            )
        )
    return indice


def construir_indice_en_memoria(directorio: Path | None = None) -> list[ChunkIndizado]:
    """
    Obtiene el índice del corpus: carga index/index.json si es válido; si no, construye y guarda.
    """
    root = directorio or directorio_corpus_defecto()
    pdfs = listar_pdfs_corpus(root)
    path_idx = ruta_index_json()

    if not pdfs:
        return []

    cargado = _intentar_cargar_indice(path_idx, root, pdfs)
    if cargado is not None:
        return cargado

    indice = _construir_indice_desde_pdfs(root, pdfs)
    if indice:
        _guardar_indice_json(path_idx, root, pdfs, indice)
    return indice


def _coseno(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _chunk_a_fragmento(
    ch: ChunkIndizado,
    score: float,
    sim_semantica: float,
    score_rerank: float | None = None,
) -> Fragmento:
    return Fragmento(
        chunk_id=ch.chunk_id,
        texto=ch.texto,
        score=score,
        sim_semantica=sim_semantica,
        score_rerank=score_rerank,
        archivo=ch.archivo,
        dominio=ch.dominio,
        tipo_doc=ch.tipo_doc,
        pagina=ch.pagina,
        pagina_fin=ch.pagina_fin,
        tipo=ch.tipo,
        titulo=ch.titulo or "",
        confidence=ch.confidence,
        articulo=ch.articulo,
        numeral=ch.numeral,
        inciso=ch.inciso,
    )


def buscar_en_corpus(
    pregunta: str,
    directorio: Path | None = None,
    dominio: str | None = None,
) -> list[Fragmento]:
    indice = construir_indice_en_memoria(directorio)
    if not indice:
        return []

    q = embed_text(pregunta)
    terminos = _terminos_consulta(pregunta)
    intencion = _intencion_consulta(pregunta)
    puntuados: list[Fragmento] = []
    for ch in indice:
        sem = _coseno(q, ch.embedding)
        base = _score_final_hibrido(sem, ch.texto, terminos)
        final = _ajustar_score_por_tipo(base, ch.tipo, pregunta)
        final = _boost_score_por_intencion(final, ch.tipo, intencion)
        puntuados.append(_chunk_a_fragmento(ch, final, sem))
    # Orden por score (semántico + keyword + ajuste por tipo + boost intención); confidence no interviene.
    puntuados.sort(key=lambda f: (-f.score, f.archivo.lower(), f.pagina))

    filtro = (dominio or "").strip()
    if filtro:
        filtrados = [f for f in puntuados if _fragmento_coincide_dominio(f, filtro)]
        if not filtrados:
            _LOG.warning(
                "buscar_en_corpus: filtro dominio=%r sin resultados; fallback búsqueda global",
                filtro,
            )
        else:
            puntuados = filtrados
    pool = _merge_pool_multivista(puntuados, indice, pregunta)
    ranked = _rerank_top_k_fragmentos(pregunta, pool, terminos)
    try:
        from cross_encoder_rerank import aplicar_rerank_cross_encoder

        ranked_ce, ce_ok = aplicar_rerank_cross_encoder(
            pregunta, ranked, indice_corpus=indice
        )
    except ImportError:
        ce_ok = False
        ranked_ce = ranked
    if ce_ok:
        out = ranked_ce
    else:
        out = _promover_top1_pairwise(ranked)
    _rag_debug_imprimir_busqueda(pregunta, ranked, out, cross_encoder_ok=ce_ok)
    return out[:TOP_K_OUTPUT]


def _fragmento_coincide_dominio(fr: Fragmento, filtro: str) -> bool:
    """Incluye el dominio pedido y siempre la carpeta ``transversal``."""
    return fr.dominio == filtro or fr.dominio == "transversal"


def buscar_fragmentos(pregunta: str, ruta_pdf: str) -> list[Fragmento]:
    ruta = Path(ruta_pdf)
    nombre = ruta.name
    paginas = extraer_texto_por_paginas(str(ruta.resolve()))
    bloques = _chunks_estructurados(paginas)
    if not bloques:
        return []

    textos = [b[0] for b in bloques]
    vectores = _embed_batch(textos, batch_size=16)
    q = embed_text(pregunta)

    tmp_chunks: list[ChunkIndizado] = []
    for ord_i, ((texto, pi, pf, tipo, titulo), vec) in enumerate(zip(bloques, vectores)):
        citas = extraer_citas_normativas(texto)
        tnorm = _normalizar_tipo(tipo)
        tit = (titulo or "")[:200]
        tmp_chunks.append(
            ChunkIndizado(
                chunk_id=_generar_chunk_id(nombre, pi, pf, ord_i, texto, tnorm, tit),
                texto=texto,
                embedding=vec,
                archivo=nombre,
                dominio="",
                tipo_doc="",
                pagina=pi,
                pagina_fin=pf,
                tipo=tnorm,
                titulo=tit,
                confidence=_confidence_por_chunk(texto, citas),
                articulo=citas["articulo"],
                numeral=citas["numeral"],
                inciso=citas["inciso"],
            )
        )

    terminos = _terminos_consulta(pregunta)
    intencion = _intencion_consulta(pregunta)
    puntuados: list[Fragmento] = []
    for ch in tmp_chunks:
        sem = _coseno(q, ch.embedding)
        base = _score_final_hibrido(sem, ch.texto, terminos)
        final = _ajustar_score_por_tipo(base, ch.tipo, pregunta)
        final = _boost_score_por_intencion(final, ch.tipo, intencion)
        puntuados.append(_chunk_a_fragmento(ch, final, sem))
    # Misma política que buscar_en_corpus: orden por score de consulta, no por confidence.
    puntuados.sort(key=lambda f: (-f.score, f.pagina))
    pool = _merge_pool_multivista(puntuados, tmp_chunks, pregunta)
    ranked = _rerank_top_k_fragmentos(pregunta, pool, terminos)
    try:
        from cross_encoder_rerank import aplicar_rerank_cross_encoder

        ranked_ce, ce_ok = aplicar_rerank_cross_encoder(
            pregunta, ranked, indice_corpus=tmp_chunks
        )
    except ImportError:
        ce_ok = False
        ranked_ce = ranked
    if ce_ok:
        out = ranked_ce
    else:
        out = _promover_top1_pairwise(ranked)
    _rag_debug_imprimir_busqueda(pregunta, ranked, out, cross_encoder_ok=ce_ok)
    return out[:TOP_K_OUTPUT]
