"""
Lectura de texto por PDF con cache en disco.

Estrategia:
  1. Intentar capa de texto nativa (PyMuPDF) en todas las páginas.
  2. Si hay páginas con texto insuficiente → fallback OCR adaptativo
     (`ocr_adaptive_engine.process_pdf_adaptive`) solo sobre el PDF completo.
  3. Guardar resultado final (texto concatenado + meta por página) en
     `{procesado}/ocr_cache/{archivo}.txt` y `.meta.json`.

Re-ejecutar no reprocesa: si la cache existe y el sha1 coincide, se reutiliza.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

_MIN_CHARS_PAGE_NATIVE = 40


@dataclass
class PaginaTexto:
    pagina: int
    motor: str          # "pymupdf_native" | "tesseract_baseline" | "docling" | "easyocr_raster" | "sin_texto"
    len_texto: int
    status: str


@dataclass
class DocumentoTexto:
    archivo: str
    sha1: str
    total_paginas: int
    paginas_con_texto: int
    len_total: int
    fecha_lectura: str
    paginas: list[PaginaTexto]
    texto_concatenado_path: str


def _ts_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _read_native(pdf_path: Path) -> list[dict]:
    import fitz

    doc = fitz.open(str(pdf_path))
    out: list[dict] = []
    for i, page in enumerate(doc, start=1):
        t = (page.get_text("text") or "").strip()
        out.append(
            {
                "pagina": i,
                "texto": t,
                "motor": "pymupdf_native" if len(t) >= _MIN_CHARS_PAGE_NATIVE else "sin_texto",
                "status": "ok" if len(t) >= _MIN_CHARS_PAGE_NATIVE else "texto_insuficiente",
            }
        )
    doc.close()
    return out


def _run_adaptive(pdf_path: Path) -> list[dict]:
    """Wrapper de ocr_adaptive_engine para documentos escaneados."""
    scripts_dir = str(Path(__file__).resolve().parent.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from ocr_adaptive_engine import process_pdf_adaptive, AdaptiveOcrConfig

    cfg = AdaptiveOcrConfig(enable_docling=False, enable_easyocr=False)
    rows = process_pdf_adaptive(pdf_path, config=cfg, write_logs=False)
    return [
        {
            "pagina": r["pagina"],
            "texto": r.get("texto", "") or "",
            "motor": r.get("motor_usado", "tesseract_baseline"),
            "status": r.get("status", ""),
        }
        for r in rows
    ]


def read_pdf_with_cache(
    pdf_path: Path | str,
    sha1: str,
    cache_dir: Path | str,
    *,
    force: bool = False,
) -> DocumentoTexto:
    """
    Devuelve metadatos + ruta al archivo .txt con texto concatenado.

    Cache hit cuando `{cache_dir}/{nombre}.meta.json` existe y su sha1 coincide.
    """
    pdf = Path(pdf_path).resolve()
    cache = Path(cache_dir).resolve()
    cache.mkdir(parents=True, exist_ok=True)

    txt_path = cache / f"{pdf.name}.txt"
    meta_path = cache / f"{pdf.name}.meta.json"

    if not force and meta_path.exists() and txt_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            if prev.get("sha1") == sha1:
                prev["texto_concatenado_path"] = str(txt_path)
                return DocumentoTexto(
                    archivo=prev["archivo"],
                    sha1=prev["sha1"],
                    total_paginas=prev["total_paginas"],
                    paginas_con_texto=prev["paginas_con_texto"],
                    len_total=prev["len_total"],
                    fecha_lectura=prev["fecha_lectura"],
                    paginas=[PaginaTexto(**p) for p in prev["paginas"]],
                    texto_concatenado_path=str(txt_path),
                )
        except Exception:
            pass

    pages_native = _read_native(pdf)
    n_insuf = sum(1 for p in pages_native if p["motor"] == "sin_texto")
    needs_ocr = n_insuf >= max(1, len(pages_native) // 3)

    if needs_ocr:
        pages = _run_adaptive(pdf)
    else:
        pages = pages_native

    parts: list[str] = []
    for p in pages:
        parts.append(f"\n\n===== PAGE {p['pagina']} (motor={p['motor']}) =====\n")
        parts.append(p.get("texto", "") or "")
    txt_path.write_text("".join(parts), encoding="utf-8")

    paginas_meta = [
        PaginaTexto(
            pagina=p["pagina"],
            motor=p.get("motor", ""),
            len_texto=len(p.get("texto", "") or ""),
            status=p.get("status", ""),
        )
        for p in pages
    ]
    doc_meta = DocumentoTexto(
        archivo=pdf.name,
        sha1=sha1,
        total_paginas=len(pages),
        paginas_con_texto=sum(1 for p in paginas_meta if p.len_texto > 0),
        len_total=sum(p.len_texto for p in paginas_meta),
        fecha_lectura=_ts_iso(),
        paginas=paginas_meta,
        texto_concatenado_path=str(txt_path),
    )
    meta_path.write_text(
        json.dumps(asdict(doc_meta), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return doc_meta


def load_texto_concatenado(meta: DocumentoTexto) -> str:
    return Path(meta.texto_concatenado_path).read_text(encoding="utf-8", errors="replace")
