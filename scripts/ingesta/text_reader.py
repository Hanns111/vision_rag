"""
Lectura de texto por PDF con decisión por-página y cache en disco.

Estrategia (v2, OCR por-página):
  Para cada página:
    1. Extraer capa de texto nativa con PyMuPDF.
    2. Si `len(texto_nativo.strip()) < 50` → aplicar OCR (Tesseract) SOLO a esa página.
    3. Registrar el motor realmente usado en `paginas[].motor`.
  Un único motor por página → sin duplicación de contenido.

  Guardar el texto concatenado (con marcadores `===== PAGE N (motor=...) =====`)
  en `{procesado}/ocr_cache/{archivo}.txt` y un `.meta.json` con trazabilidad
  por página (len, motor, status).

  Cache-hit por sha1 del PDF: re-ejecutar no reprocesa si el archivo no cambió.
  `--force` invalida el cache completo (política todo-o-nada por simplicidad).

Principios:
  - Idempotente: mismo sha1 + mismo umbral → mismo texto.
  - Sin duplicación: cada página se incluye una sola vez con un solo motor.
  - Tolerante a falla: si OCR de una página revienta, la página queda vacía
    con `status = error_tesseract_pagina` y el pipeline continúa.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Umbral mínimo de caracteres útiles en texto nativo para NO aplicar OCR a esa página.
# Páginas con menos chars que este umbral se OCR-izan con Tesseract.
_MIN_CHARS_PAGE_NATIVE = 50


@dataclass
class PaginaTexto:
    pagina: int
    motor: str          # "pymupdf_native" | "tesseract_baseline" | "sin_texto_ocr_fallido"
    len_texto: int
    status: str


@dataclass
class DocumentoTexto:
    archivo: str
    sha1: str
    total_paginas: int
    paginas_con_texto: int
    paginas_nativas: int
    paginas_ocr: int
    len_total: int
    fecha_lectura: str
    paginas: list[PaginaTexto]
    texto_concatenado_path: str


def _ts_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _ocr_una_pagina(pdf_path: Path, page_1based: int) -> tuple[str, str]:
    """
    OCR Tesseract sobre UNA página. Reusa el helper del pipeline baseline.
    Devuelve (texto, status).
    """
    scripts_dir = str(Path(__file__).resolve().parent.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import fitz  # PyMuPDF
        from document_ocr_runner import process_image, _render_page_bgr

        doc = fitz.open(str(pdf_path))
        try:
            page = doc.load_page(page_1based - 1)
            bgr = _render_page_bgr(page)
        finally:
            doc.close()
        texto, status = process_image(bgr)
        return texto or "", status or ("ok" if texto else "ocr_vacio")
    except Exception as exc:
        return "", f"error_tesseract_pagina:{exc!s}"


def _leer_pdf_por_pagina(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Para cada página: intenta nativo; si < umbral, aplica OCR a esa página.
    """
    import fitz

    out: list[dict[str, Any]] = []
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        return [{"pagina": 0, "texto": "", "motor": "error_apertura",
                 "status": f"error_apertura:{exc!s}"}]

    try:
        n_pages = len(doc)
        for i in range(1, n_pages + 1):
            page = doc.load_page(i - 1)
            t_nat = (page.get_text("text") or "").strip()
            if len(t_nat) >= _MIN_CHARS_PAGE_NATIVE:
                out.append({
                    "pagina": i,
                    "texto": t_nat,
                    "motor": "pymupdf_native",
                    "status": "ok",
                })
                continue
            # Nativo insuficiente → OCR solo esta página
            # Nota: abrimos/cerramos dentro de _ocr_una_pagina para no
            # mantener referencias al documento durante la rasterización
            t_ocr, status = _ocr_una_pagina(pdf_path, i)
            if t_ocr:
                out.append({
                    "pagina": i,
                    "texto": t_ocr,
                    "motor": "tesseract_baseline",
                    "status": status,
                })
            else:
                out.append({
                    "pagina": i,
                    "texto": "",
                    "motor": "sin_texto_ocr_fallido",
                    "status": status,
                })
    finally:
        doc.close()

    return out


def read_pdf_with_cache(
    pdf_path: Path | str,
    sha1: str,
    cache_dir: Path | str,
    *,
    force: bool = False,
) -> DocumentoTexto:
    """
    Lee un PDF con decisión por-página (nativo o OCR) y devuelve metadatos
    + ruta al archivo .txt concatenado. Cache por sha1.
    """
    pdf = Path(pdf_path).resolve()
    cache = Path(cache_dir).resolve()
    cache.mkdir(parents=True, exist_ok=True)

    txt_path = cache / f"{pdf.name}.txt"
    meta_path = cache / f"{pdf.name}.meta.json"

    if not force and meta_path.exists() and txt_path.exists():
        try:
            prev = json.loads(meta_path.read_text(encoding="utf-8"))
            if prev.get("sha1") == sha1 and prev.get("schema_version") == "text_reader.v2":
                prev["texto_concatenado_path"] = str(txt_path)
                return DocumentoTexto(
                    archivo=prev["archivo"],
                    sha1=prev["sha1"],
                    total_paginas=prev["total_paginas"],
                    paginas_con_texto=prev["paginas_con_texto"],
                    paginas_nativas=prev.get("paginas_nativas", 0),
                    paginas_ocr=prev.get("paginas_ocr", 0),
                    len_total=prev["len_total"],
                    fecha_lectura=prev["fecha_lectura"],
                    paginas=[PaginaTexto(**p) for p in prev["paginas"]],
                    texto_concatenado_path=str(txt_path),
                )
        except Exception:
            pass

    pages = _leer_pdf_por_pagina(pdf)

    # Concatenar con marcadores. Formato compatible con id_resolver / classifier.
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
        paginas_nativas=sum(1 for p in paginas_meta if p.motor == "pymupdf_native"),
        paginas_ocr=sum(1 for p in paginas_meta if p.motor == "tesseract_baseline"),
        len_total=sum(p.len_texto for p in paginas_meta),
        fecha_lectura=_ts_iso(),
        paginas=paginas_meta,
        texto_concatenado_path=str(txt_path),
    )
    payload = asdict(doc_meta)
    payload["schema_version"] = "text_reader.v2"
    payload["umbral_chars_nativo"] = _MIN_CHARS_PAGE_NATIVE
    meta_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return doc_meta


def load_texto_concatenado(meta: DocumentoTexto) -> str:
    return Path(meta.texto_concatenado_path).read_text(encoding="utf-8", errors="replace")
