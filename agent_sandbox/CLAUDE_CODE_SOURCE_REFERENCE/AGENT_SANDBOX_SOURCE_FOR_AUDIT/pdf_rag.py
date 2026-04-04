"""Corpus PDF multi-documento: chunks con metadatos y citas, índice en JSON local, ranking híbrido.

Campo ``confidence`` (índice JSON, :class:`ChunkIndizado`, :class:`Fragmento`):
    Representa **únicamente** una heurística de **calidad de extracción** del fragmento
    (texto obtenido del PDF vía PyMuPDF y patrones detectables), no otra cosa.

    **No representa:** veracidad del contenido, corrección jurídica, vigencia normativa
    ni idoneidad legal del texto para un caso concreto.

    **Ranking de recuperación:** el orden de los resultados **no** usa ``confidence``;
    se ordena por ``score`` = (similitud coseno + ``KEYWORD_WEIGHT`` × keywords),
    luego multiplicadores por ``tipo`` de chunk (p. ej. penalizar ``indice``, reforzar
    ``objetivo`` / ``articulo``). ``confidence`` es metadato de trazabilidad / auditoría.

    **Diseño futuro (no implementado):** separar señales explícitas, p. ej.
    ``extraction_confidence`` (lo que hoy se persiste como ``confidence``),
    ``semantic_score`` (por consulta, p. ej. coseno con la pregunta),
    ``legal_relevance`` (rerank o validación jurídica futura).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from embeddings import MODEL_ID, _embed_batch, embed_text

INDEX_SCHEMA_VERSION = 2

# Tipos de chunk (heurísticas sin LLM). Debe coincidir con serialización y ranking.
TIPO_OBJETIVO = "objetivo"
TIPO_ARTICULO = "articulo"
TIPO_NUMERAL = "numeral"
TIPO_INDICE = "indice"
TIPO_ANEXO = "anexo"
TIPO_TEXTO_GENERAL = "texto_general"
TIPOS_VALIDOS = frozenset(
    {
        TIPO_OBJETIVO,
        TIPO_ARTICULO,
        TIPO_NUMERAL,
        TIPO_INDICE,
        TIPO_ANEXO,
        TIPO_TEXTO_GENERAL,
    }
)
# Desempate al agrupar palabras en un chunk (~400 palabras): preferir valor normativo.
_TIPO_PRIORIDAD_RANK = (
    TIPO_OBJETIVO,
    TIPO_ARTICULO,
    TIPO_NUMERAL,
    TIPO_ANEXO,
    TIPO_TEXTO_GENERAL,
    TIPO_INDICE,
)

CHUNK_TARGET_WORDS = 400
TOP_K = 5
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


def _ajustar_score_por_tipo(score: float, tipo: str) -> float:
    """Tras score semántico + keywords, ponderar por tipo estructural del chunk."""
    t = (tipo or TIPO_TEXTO_GENERAL).strip().lower()
    if t == TIPO_INDICE:
        return score * 0.3
    if t in (TIPO_OBJETIVO, TIPO_ARTICULO):
        return score * 1.2
    return score


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
    """Resultado de búsqueda. ``score`` = híbrido + ajuste por ``tipo``; ``confidence`` = extracción (índice)."""

    chunk_id: str
    texto: str
    score: float
    archivo: str
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
        return ChunkIndizado(
            chunk_id=chunk_id,
            texto=texto,
            embedding=[float(x) for x in emb],
            archivo=str(archivo),
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
        p for p in directorio.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"
    )


# --- Chunking estructural (sin LLM): TOC, objetivo, artículo, numeral, anexo, secciones ---

_RE_TITULO_INDICE = re.compile(
    r"^(ÍNDICE|INDICE|TABLA\s+DE\s+CONTENIDO|CONTENIDO)\s*$",
    re.IGNORECASE,
)
_RE_SEC_COMPUESTO = re.compile(r"^\s*\d+\.\d+(?:\.\d+)*\s+\S")
_RE_SEC_SIMPLE = re.compile(r"^\s*\d+\.\s+\S")
_RE_ANEXO_LINE = re.compile(r"^ANEXO\s", re.IGNORECASE)
_RE_ART_LINE_START = re.compile(r"^Art[ií]culo\s+\d+", re.IGNORECASE)
_RE_NUM_LINE_START = re.compile(r"^Numeral\s+\d", re.IGNORECASE)


def _es_entrada_toc(line: str) -> bool:
    s = (line or "").strip()
    if not s or _RE_TITULO_INDICE.match(s):
        return False
    return bool(re.search(r"\.{2,}\s*\d+\s*$", s))


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


@dataclass
class _EstadoChunkingEstructural:
    active_tipo: str = TIPO_TEXTO_GENERAL
    active_titulo: str = ""
    in_toc_block: bool = False


def _actualizar_estado_por_linea(st: _EstadoChunkingEstructural, line: str) -> None:
    s = (line or "").strip()
    if not s:
        return

    if _RE_TITULO_INDICE.match(s):
        st.in_toc_block = True
        st.active_tipo = TIPO_INDICE
        st.active_titulo = s[:200]
        return

    if st.in_toc_block:
        if _es_entrada_toc(s):
            st.active_tipo = TIPO_INDICE
            st.active_titulo = s[:200]
            return
        if _es_encabezado_seccion(s):
            st.in_toc_block = False
        else:
            st.active_tipo = TIPO_INDICE
            return

    if _es_entrada_toc(s):
        st.active_tipo = TIPO_INDICE
        st.active_titulo = s[:200]
        return

    if _RE_ANEXO_LINE.match(s):
        st.active_tipo = TIPO_ANEXO
        st.active_titulo = s[:200]
        return

    if _RE_ART_LINE_START.match(s):
        st.active_tipo = TIPO_ARTICULO
        st.active_titulo = s[:200]
        return

    if _RE_NUM_LINE_START.match(s):
        st.active_tipo = TIPO_NUMERAL
        st.active_titulo = s[:200]
        return

    if _es_encabezado_seccion(s):
        st.active_titulo = s[:200]
        st.active_tipo = TIPO_OBJETIVO if _tiene_objetivo(s) else TIPO_TEXTO_GENERAL
        return

    if _es_mayusculas_titulo(s):
        st.active_titulo = s[:200]
        return


def _stream_palabras_etiquetadas(
    paginas: list[tuple[int, str]],
) -> list[tuple[str, int, str, str]]:
    st = _EstadoChunkingEstructural()
    out: list[tuple[str, int, str, str]] = []
    for num_pagina, texto_pag in paginas:
        for line in (texto_pag or "").splitlines():
            _actualizar_estado_por_linea(st, line)
            for w in re.findall(r"\S+", line.strip()):
                out.append((w, num_pagina, st.active_tipo, st.active_titulo))
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
                titulo_dom = tit_w[:200]
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
            tipo_final = _tipo_mayoritario(counts)
            tnorm = _normalizar_tipo(tipo_final)
            titulo_out = _titulo_del_tipo_dominante(buf, tnorm)
            bloques.append((texto, p_min, p_max or p_min, tnorm, titulo_out))
        buf = []
        p_min = p_max = None
        counts.clear()

    for w, pg, tipo_w, titulo_w in stream:
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
            tipo_final = _tipo_mayoritario(counts)
            tnorm = _normalizar_tipo(tipo_final)
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
        indice.append(
            ChunkIndizado(
                chunk_id=cid,
                texto=texto,
                embedding=vec,
                archivo=archivo,
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


def _chunk_a_fragmento(ch: ChunkIndizado, score: float) -> Fragmento:
    return Fragmento(
        chunk_id=ch.chunk_id,
        texto=ch.texto,
        score=score,
        archivo=ch.archivo,
        pagina=ch.pagina,
        pagina_fin=ch.pagina_fin,
        tipo=ch.tipo,
        titulo=ch.titulo or "",
        confidence=ch.confidence,
        articulo=ch.articulo,
        numeral=ch.numeral,
        inciso=ch.inciso,
    )


def buscar_en_corpus(pregunta: str, directorio: Path | None = None) -> list[Fragmento]:
    indice = construir_indice_en_memoria(directorio)
    if not indice:
        return []

    q = embed_text(pregunta)
    terminos = _terminos_consulta(pregunta)
    puntuados: list[Fragmento] = []
    for ch in indice:
        sem = _coseno(q, ch.embedding)
        base = _score_final_hibrido(sem, ch.texto, terminos)
        final = _ajustar_score_por_tipo(base, ch.tipo)
        puntuados.append(_chunk_a_fragmento(ch, final))
    # Orden por score (semántico + keyword + ajuste por tipo); confidence no interviene.
    puntuados.sort(key=lambda f: (-f.score, f.archivo.lower(), f.pagina))
    return puntuados[:TOP_K]


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
    puntuados: list[Fragmento] = []
    for ch in tmp_chunks:
        sem = _coseno(q, ch.embedding)
        base = _score_final_hibrido(sem, ch.texto, terminos)
        final = _ajustar_score_por_tipo(base, ch.tipo)
        puntuados.append(_chunk_a_fragmento(ch, final))
    # Misma política que buscar_en_corpus: orden por score de consulta, no por confidence.
    puntuados.sort(key=lambda f: (-f.score, f.pagina))
    return puntuados[:TOP_K]
