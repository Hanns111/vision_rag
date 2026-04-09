"""Segunda etapa: re-ranking con cross-encoder BGE (GPU). No modifica embeddings del índice."""

from __future__ import annotations

import logging
import math
import os
import re
import unicodedata
from collections import defaultdict
from dataclasses import replace
from typing import Any

_LOG = logging.getLogger(__name__)

MODEL_ID = "BAAI/bge-reranker-v2-m3"
# Texto muy largo se trunca vía max_length del modelo (512 tokens por defecto en CrossEncoder).
_MAX_TEXT_CHARS = 12000
# Vecinos: ~60–75 tokens por lado (~250 caracteres en español).
_MAX_VECINO_CHARS = 280
# Ventana de ``score_rerank`` dentro de la cual el desempate estructural puede reordenar.
_CE_BUCKET = 0.04

_ce_singleton: Any = None


def _cross_encoder_enabled() -> bool:
    v = (os.environ.get("AGENT_CROSS_ENCODER") or "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _get_cross_encoder():
    global _ce_singleton
    if _ce_singleton is not None:
        return _ce_singleton
    import torch
    from sentence_transformers import CrossEncoder

    if not torch.cuda.is_available():
        raise RuntimeError("Cross-encoder: CUDA no disponible (se requiere GPU)")
    _ce_singleton = CrossEncoder(
        MODEL_ID,
        device="cuda",
        max_length=1024,
    )
    m = getattr(_ce_singleton, "model", None)
    if m is not None:
        m.eval()
    return _ce_singleton


def _agrupar_indice_por_archivo(indice: list[Any]) -> dict[str, list[Any]]:
    m: dict[str, list[Any]] = defaultdict(list)
    for ch in indice or []:
        a = getattr(ch, "archivo", "") or ""
        m[a].append(ch)
    for arch, lst in m.items():
        lst.sort(
            key=lambda c: (
                getattr(c, "pagina", 0),
                getattr(c, "pagina_fin", 0),
                getattr(c, "chunk_id", ""),
            )
        )
    return dict(m)


def _tail_chars(s: str, n: int) -> str:
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[-n:].strip()


def _head_chars(s: str, n: int) -> str:
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[:n].strip()


def texto_expandido_cross_encoder(fr: Any, por_archivo: dict[str, list[Any]]) -> str:
    """
    ``chunk_prev`` tail + ``chunk_actual`` + ``chunk_next`` head.
    No altera metadatos del fragmento; solo el texto pasado al modelo CE.
    """
    cur = (getattr(fr, "texto", None) or "").strip()
    arch = getattr(fr, "archivo", "") or ""
    cid = getattr(fr, "chunk_id", "")
    arr = por_archivo.get(arch, [])
    idx = next(
        (i for i, c in enumerate(arr) if getattr(c, "chunk_id", None) == cid),
        -1,
    )
    if idx < 0:
        return cur
    parts: list[str] = []
    if idx > 0:
        prev_t = getattr(arr[idx - 1], "texto", "") or ""
        t = _tail_chars(prev_t, _MAX_VECINO_CHARS)
        if t:
            parts.append(t)
    parts.append(cur)
    if idx + 1 < len(arr):
        next_t = getattr(arr[idx + 1], "texto", "") or ""
        h = _head_chars(next_t, _MAX_VECINO_CHARS)
        if h:
            parts.append(h)
    return "\n\n".join(parts)


_STOP_TB = frozenset(
    {
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "de",
        "del",
        "en",
        "y",
        "o",
        "a",
        "al",
        "que",
        "por",
        "para",
        "con",
        "sin",
        "se",
        "es",
        "son",
    }
)


def _tiebreak_estructural(pregunta: str, fr: Any) -> float:
    """
    Desempate adicional (no sustituye ``score_rerank``): cobertura léxica, dígitos, marcas normativas.
    """
    q = (pregunta or "").lower()
    qn = unicodedata.normalize("NFD", q)
    q_fold = "".join(c for c in qn if unicodedata.category(c) != "Mn")
    low = (
        (getattr(fr, "texto", None) or "")
        + " "
        + (getattr(fr, "titulo", None) or "")
    ).lower()
    ln = unicodedata.normalize("NFD", low)
    low_fold = "".join(c for c in ln if unicodedata.category(c) != "Mn")

    tb = 0.0
    terms = re.findall(r"[a-záéíóúüñ0-9]{2,}", q_fold, flags=re.IGNORECASE)
    for t in terms:
        tl = t.lower()
        if tl in _STOP_TB or len(tl) < 3:
            continue
        try:
            if re.search(r"\b" + re.escape(tl) + r"\b", low_fold, flags=re.IGNORECASE):
                tb += 1.0 + min(2.0, len(tl) * 0.06)
        except re.error:
            continue

    q_digits = re.findall(r"\d+", q_fold)
    if q_digits:
        for d in q_digits:
            if len(d) >= 1 and d in low_fold:
                tb += 1.8
                break

    for w in (
        "articulo",
        "numeral",
        "inciso",
        "directiva",
        "disposicion",
        "resolucion",
    ):
        if w in low_fold:
            tb += 0.35

    return tb


def _ordenar_por_ce_y_desempate(
    anotados: list[Any],
    pregunta: str,
) -> list[Any]:
    """``score_rerank`` domina; dentro del mismo cubo (_CE_BUCKET) manda el desempate estructural."""
    if len(anotados) <= 1:
        return anotados
    tbs = [_tiebreak_estructural(pregunta, fr) for fr in anotados]
    mx = max(tbs) if tbs else 1.0
    mx = mx if mx > 1e-9 else 1.0

    def sort_key(fr: Any, i: int) -> tuple:
        sr = float(getattr(fr, "score_rerank", None) or 0.0)
        bucket = math.floor(sr / _CE_BUCKET + 1e-12)
        tb = tbs[i] / mx
        return (
            -bucket,
            -tb,
            -sr,
            -float(getattr(fr, "score", 0.0)),
            fr.archivo.lower(),
            fr.pagina,
        )

    indexed = list(enumerate(anotados))
    indexed.sort(key=lambda ix: sort_key(ix[1], ix[0]))
    return [x[1] for x in indexed]


def aplicar_rerank_cross_encoder(
    pregunta: str,
    fragmentos: list[Any],
    indice_corpus: list[Any] | None = None,
) -> tuple[list[Any], bool]:
    """
    Asigna ``score_rerank`` a cada fragmento y devuelve la lista ordenada por ese score (desc).

    Si ``indice_corpus`` se pasa (chunks del mismo corpus), el par query–documento usa
    contexto local (cola/cabeza de vecinos) solo para inferencia CE.

    Si falla import, CUDA o inferencia, devuelve ``(fragmentos, False)`` sin modificar.
    """
    if not fragmentos:
        return fragmentos, False
    if not _cross_encoder_enabled():
        return fragmentos, False

    try:
        import torch

        if not torch.cuda.is_available():
            _LOG.debug("cross_encoder: omitido (sin CUDA)")
            return fragmentos, False
    except Exception:
        return fragmentos, False

    q = (pregunta or "").strip()
    if not q:
        return fragmentos, False

    try:
        model = _get_cross_encoder()
    except Exception as exc:  # noqa: BLE001
        _LOG.warning("cross_encoder: no se pudo cargar modelo: %s", exc)
        return fragmentos, False

    por_arch: dict[str, list[Any]] | None = None
    if indice_corpus:
        por_arch = _agrupar_indice_por_archivo(indice_corpus)

    pairs: list[list[str]] = []
    for fr in fragmentos:
        if por_arch:
            t = texto_expandido_cross_encoder(fr, por_arch).strip()
        else:
            t = (getattr(fr, "texto", None) or "").strip()
        if len(t) > _MAX_TEXT_CHARS:
            t = t[:_MAX_TEXT_CHARS]
        pairs.append([q, t])

    try:
        import numpy as np
        import torch

        with torch.inference_mode():
            raw = model.predict(
                pairs,
                batch_size=min(8, len(pairs)),
                show_progress_bar=False,
                convert_to_numpy=True,
            )
    except Exception as exc:  # noqa: BLE001
        _LOG.warning("cross_encoder: inferencia fallida: %s", exc)
        return fragmentos, False

    try:
        import numpy as np

        arr = np.asarray(raw, dtype=np.float64).reshape(-1)
        scores = [float(x) for x in arr]
    except (TypeError, ValueError):
        scores = [float(raw)] if len(fragmentos) == 1 else list(raw)

    if len(scores) != len(fragmentos):
        _LOG.warning(
            "cross_encoder: len(scores)=%s != len(frag)=%s",
            len(scores),
            len(fragmentos),
        )
        return fragmentos, False

    anotados: list[Any] = []
    for fr, sc in zip(fragmentos, scores, strict=True):
        anotados.append(replace(fr, score_rerank=sc))

    anotados = _ordenar_por_ce_y_desempate(anotados, q)
    return anotados, True
