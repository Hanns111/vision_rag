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
# DPI al rasterizar páginas escaneadas para OCR (baseline 300; subir invalida
# cache y altera el resultado de páginas que ya funcionan).
_OCR_RENDER_DPI = 300
# Umbral CONSERVADOR para activar reintentos: solo páginas casi vacías o con
# mucha basura Unicode. Así no se toca el OCR de páginas que ya funcionan bien.
_MIN_CHARS_FIRST_PASS = 60
_MAX_JUNK_RATIO_FIRST_PASS = 0.03


def _to_gray(bgr: np.ndarray) -> np.ndarray:
    if len(bgr.shape) == 2:
        return bgr
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def _clahe(gray: np.ndarray, clip: float = 3.5) -> np.ndarray:
    return cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(gray)


def _denoise(gray: np.ndarray) -> np.ndarray:
    # fastNlMeansDenoising es caro pero efectivo en escaneados grises tenues.
    return cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)


def _unsharp(gray: np.ndarray, amount: float = 1.2) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (0, 0), sigmaX=1.2)
    sharp = cv2.addWeighted(gray, 1 + amount, blur, -amount, 0)
    return np.clip(sharp, 0, 255).astype(np.uint8)


def _adaptive_binarize(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )


def _auto_rotate(gray: np.ndarray) -> np.ndarray:
    """Si tesseract OSD detecta 90/180/270, rota. Silencioso ante fallo."""
    try:
        osd = pytesseract.image_to_osd(gray, config="--psm 0")
        import re as _re
        m = _re.search(r"Rotate: (\d+)", osd or "")
        rot = int(m.group(1)) if m else 0
    except Exception:
        rot = 0
    if rot == 90:
        return cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if rot == 180:
        return cv2.rotate(gray, cv2.ROTATE_180)
    if rot == 270:
        return cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
    return gray


def _normalize_for_ocr(bgr: np.ndarray) -> np.ndarray:
    """Pasada conservadora (compat con baseline previo): gris + CLAHE suave."""
    if bgr is None or bgr.size == 0:
        return bgr
    gray = _to_gray(bgr)
    return _clahe(gray, clip=2.0)


def _enhanced_for_ocr(bgr: np.ndarray) -> np.ndarray:
    """Pasada intermedia: denoise + CLAHE moderado + unsharp (sin binarizar)."""
    if bgr is None or bgr.size == 0:
        return bgr
    gray = _to_gray(bgr)
    gray = _denoise(gray)
    gray = _clahe(gray, clip=3.0)
    gray = _unsharp(gray, amount=0.8)
    return gray


def _aggressive_for_ocr(bgr: np.ndarray) -> np.ndarray:
    """Pasada agresiva: upscale 2x + CLAHE fuerte + unsharp (sin binarizar)."""
    if bgr is None or bgr.size == 0:
        return bgr
    gray = _to_gray(bgr)
    gray = _denoise(gray)
    h, w = gray.shape[:2]
    gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    gray = _clahe(gray, clip=4.0)
    gray = _unsharp(gray, amount=1.2)
    return gray


def _tess(img: np.ndarray, psm: int | None = None) -> str:
    """psm=None → default de Tesseract (PSM 3, auto). Compatible con baseline."""
    cfg = ""
    if psm is not None:
        cfg = f"--oem 1 --psm {psm}"
    return (pytesseract.image_to_string(img, lang="spa+eng", config=cfg) or "").strip()


def _junk_ratio(s: str) -> float:
    """Proporción de caracteres 'basura' Unicode (replacement char + diamantes)."""
    if not s:
        return 1.0
    junk = sum(1 for c in s if c in "\ufffd")
    return junk / max(len(s), 1)


def process_image(img: np.ndarray | None) -> tuple[str, str]:
    """
    OCR de una imagen BGR (OpenCV), multi-pasada NO destructiva.

    Principio: la PRIMERA pasada replica el baseline (CLAHE 2.0 + PSM 3 auto)
    para no regresar cobertura en páginas que antes funcionaban. Los reintentos
    solo se activan cuando la primera pasada da texto muy corto o con mucha
    basura, y solo suman texto si realmente mejoran.

      1. Pasada baseline (CLAHE suave, PSM auto).
      2. Si < _MIN_CHARS_FIRST_PASS o junk alto:
         - Reintento con preproc intermedio (denoise + CLAHE 3.0 + unsharp).
         - Reintento con auto-rotación OSD.
      3. Si sigue pobre: pasada agresiva (upscale 2x).

    Se devuelve el texto más largo entre los intentos. Status refleja qué pasada
    ganó (ok | ok_enhanced | ok_rotado | ok_agresivo).

    Returns:
        (texto_completo, status): ok | ocr_vacio | sin_imagen | error:*
    """
    if img is None:
        return "", "sin_imagen"
    try:
        gray_base = _normalize_for_ocr(img)
        text1 = _tess(gray_base, psm=None)
        best = text1
        status = "ok" if text1 else "ocr_vacio"

        needs_retry = (
            len(best) < _MIN_CHARS_FIRST_PASS
            or _junk_ratio(best) > _MAX_JUNK_RATIO_FIRST_PASS
        )
        if needs_retry:
            # Intento 2: preproc intermedio (denoise + CLAHE 3.0 + unsharp).
            gray_enh = _enhanced_for_ocr(img)
            text2 = _tess(gray_enh, psm=None)
            if len(text2) > len(best):
                best = text2
                status = "ok_enhanced"

            # Intento 3: auto-rotación sobre preproc intermedio.
            gray_rot = _auto_rotate(gray_enh)
            if gray_rot is not gray_enh:
                text3 = _tess(gray_rot, psm=None)
                if len(text3) > len(best):
                    best = text3
                    status = "ok_rotado"

            # Intento 4: pasada agresiva (upscale 2x) solo si sigue pobre.
            if len(best) < _MIN_CHARS_FIRST_PASS:
                gray_agr = _aggressive_for_ocr(img)
                text4 = _tess(gray_agr, psm=None)
                if len(text4) > len(best):
                    best = text4
                    status = "ok_agresivo"

        if not best:
            return "", "ocr_vacio"
        return best, status
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
