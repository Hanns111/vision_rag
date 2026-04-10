"""
Extracción de texto desde PDF e imágenes: capa digital (PyMuPDF) u OCR (Tesseract).

Requisitos: pip install pymupdf opencv-python pytesseract numpy
En Windows, instalar el binario de Tesseract y, si hace falta, configurar
pytesseract.pytesseract.tesseract_cmd.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import cv2
import numpy as np

try:
    import fitz  # PyMuPDF
except ImportError as e:  # pragma: no cover
    raise SystemExit("Instale pymupdf: pip install pymupdf") from e

try:
    import pytesseract
except ImportError as e:  # pragma: no cover
    raise SystemExit("Instale pytesseract: pip install pytesseract") from e

# Umbral mínimo de caracteres para considerar que la página tiene texto incrustado útil.
_MIN_TEXT_LAYER_CHARS = 40
# DPI al rasterizar páginas escaneadas para OCR.
_OCR_RENDER_DPI = 300


def _normalize_for_ocr(bgr: np.ndarray) -> np.ndarray:
    """Preprocesado conservador: escala de grises + CLAHE suave."""
    if bgr is None or bgr.size == 0:
        return bgr
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def process_image(img: np.ndarray | None) -> tuple[str, str]:
    """
    OCR de una imagen BGR (OpenCV).

    Returns:
        (texto_completo, status): status en ok | ocr_vacio | sin_imagen | error
    """
    if img is None:
        return "", "sin_imagen"
    try:
        gray = _normalize_for_ocr(img)
        # spa+eng: ajustar según corpus; por defecto español + inglés para números/siglas.
        text = pytesseract.image_to_string(gray, lang="spa+eng")
        text = (text or "").strip()
        if not text:
            return "", "ocr_vacio"
        return text, "ok"
    except Exception as exc:  # pragma: no cover - depende del entorno Tesseract
        return "", f"error:{exc!s}"


def _page_text_layer(fitz_page: fitz.Page) -> str:
    return (fitz_page.get_text("text") or "").strip()


def _render_page_bgr(fitz_page: fitz.Page, dpi: int = _OCR_RENDER_DPI) -> np.ndarray:
    """Rasteriza una página PDF a imagen BGR para OpenCV."""
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = fitz_page.get_pixmap(matrix=mat, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    else:
        arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    return arr


def process_pdf(pdf_path: str) -> list[dict[str, Any]]:
    """
    Por cada página: si hay capa de texto suficiente, la usa; si no, OCR sobre raster.

    Returns:
        Lista de dicts con pagina, status, texto (texto truncado opcional en caller).
    """
    out: list[dict[str, Any]] = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        return [
            {
                "pagina": 0,
                "status": f"error_apertura:{exc!s}",
                "texto": "",
            }
        ]

    try:
        for i in range(len(doc)):
            page = doc.load_page(i)
            n = i + 1
            layer = _page_text_layer(page)
            if len(layer) >= _MIN_TEXT_LAYER_CHARS:
                out.append(
                    {
                        "pagina": n,
                        "status": "digital_text",
                        "texto": layer,
                    }
                )
                continue

            bgr = _render_page_bgr(page)
            text, st = process_image(bgr)
            if st == "ok":
                out.append({"pagina": n, "status": "ocr", "texto": text})
            else:
                out.append({"pagina": n, "status": st, "texto": text})
    finally:
        doc.close()

    return out


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # Piloto OCR PASO 1: PDFs bajo data/piloto_ocr/raw/ (ver MANIFEST_PILOTO.csv)
    _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ruta = os.path.join(_repo_root, "data", "piloto_ocr", "raw")

    if os.path.isdir(ruta):
        archivos = sorted(os.listdir(ruta))

        for archivo in archivos:
            if archivo.lower().endswith(".pdf"):
                pdf_path = os.path.join(ruta, archivo)
                print(f"\n==============================")
                print(f"Procesando: {archivo}")
                print(f"==============================")

                resultado = process_pdf(pdf_path)

                for r in resultado:
                    print(r)

    else:
        if ruta.lower().endswith(".pdf"):
            resultado = process_pdf(ruta)
        else:
            img = cv2.imread(ruta)
            text, status = process_image(img)
            resultado = [{"pagina": 1, "status": status, "texto": text[:200]}]

        print("\nRESULTADO FINAL:")
        for r in resultado:
            print(r)

    sys.exit(0)
