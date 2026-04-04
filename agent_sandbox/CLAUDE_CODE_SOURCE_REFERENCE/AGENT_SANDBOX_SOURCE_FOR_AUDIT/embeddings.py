"""
Embeddings locales: sentence-transformers/all-MiniLM-L6-v2.
Vectores L2-normalizados → similitud coseno = producto escalar.
"""

from __future__ import annotations

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
_MODEL_NAME = MODEL_ID  # alias interno
_MODEL = None


def _get_model():  # noqa: ANN202
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "Instala sentence-transformers: pip install sentence-transformers"
            ) from exc
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_text(texto: str) -> list[float]:
    """Vector de embedding para un texto (normalizado L2)."""
    t = (texto or "").strip() or " "
    return _embed_batch([t])[0]


def _embed_batch(textos: list[str], batch_size: int = 32) -> list[list[float]]:
    if not textos:
        return []
    model = _get_model()
    arr = model.encode(
        textos,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    if arr.ndim == 1:
        return [arr.astype(float).tolist()]
    return [row.astype(float).tolist() for row in arr]
