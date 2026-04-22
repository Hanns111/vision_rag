"""
OCR dirigido a zona de totales (segunda opinión para comprobantes con
campos tributarios faltantes).

NO reemplaza el OCR principal (text_reader.v2). Se invoca post-extracción
solo cuando la primera pasada dejó campos tributarios vacíos; rellena
huecos sin sobrescribir valores ya capturados.

Estrategia:
  1. Renderiza la página completa a 500 DPI (vs 300 DPI del OCR principal).
  2. Aplica 3 variantes de preprocesamiento y corre Tesseract en cada una:
       a) 'soft'     — grayscale + CLAHE(4.0) + upscale 1.3x
       b) 'binary'   — a) + adaptive binarize
       c) 'deskew'   — b) con corrección de inclinación (<5°)
  3. Dos PSM por variante: 6 (bloque uniforme) y 4 (columna única).
  4. Devuelve el texto más largo como "mejor" resultado.

Costo: ~3-6 segundos por página. Solo se ejecuta para comprobantes con
campos faltantes, así que el overhead total es acotado.

NO inventa datos: si el texto recuperado no contiene los patrones buscados,
los campos quedan None.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


def _render_page(pdf_path: Path | str, pagina_1based: int, dpi: int = 500) -> np.ndarray | None:
    """Renderiza una página PDF a imagen BGR OpenCV al DPI indicado."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return None
    try:
        if pagina_1based < 1 or pagina_1based > len(doc):
            return None
        page = doc.load_page(pagina_1based - 1)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        else:
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        return arr
    finally:
        doc.close()


def _deskew(gray: np.ndarray, umbral_grados: float = 0.3) -> np.ndarray:
    """Corrige inclinación < 5° vía minAreaRect sobre píxeles no-blanco.
    Silencioso ante fallo; devuelve entrada si el ángulo es dudoso."""
    try:
        _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        coords = cv2.findNonZero(bw)
        if coords is None or len(coords) < 500:
            return gray
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90
        if abs(angle) < umbral_grados:
            return gray
        if abs(angle) > 5.0:
            return gray  # outlier, probablemente imagen no-texto
        h, w = gray.shape
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        return cv2.warpAffine(
            gray, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
    except Exception:
        return gray


def _preproc_soft(bgr: np.ndarray) -> np.ndarray:
    """Grayscale + CLAHE 4.0 + upscale 1.3x. Sin binarizar."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8)).apply(gray)
    gray = cv2.resize(gray, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)
    return gray


def _preproc_binary(bgr: np.ndarray) -> np.ndarray:
    """Soft + denoise + adaptive binarize."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=8, templateWindowSize=7, searchWindowSize=21)
    gray = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8)).apply(gray)
    gray = cv2.resize(gray, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )


def _preproc_deskew(bgr: np.ndarray) -> np.ndarray:
    """Binary + deskew."""
    binz = _preproc_binary(bgr)
    return _deskew(binz)


def _tess(img: np.ndarray, psm: int) -> str:
    try:
        import pytesseract
        cfg = f"--oem 1 --psm {psm}"
        return (pytesseract.image_to_string(img, lang="spa+eng", config=cfg) or "").strip()
    except Exception:
        return ""


def ocr_pagina_agresivo(pdf_path: Path | str, pagina: int) -> tuple[str, dict[str, Any]]:
    """Re-OCR de una página con preprocesamiento agresivo multi-variante.

    Returns:
        (mejor_texto, meta): meta incluye la variante ganadora y
        longitudes de cada intento para trazabilidad.
    """
    bgr = _render_page(pdf_path, pagina, dpi=500)
    if bgr is None:
        return "", {"error": "render_fallido", "intentos": {}}

    intentos: dict[str, str] = {}
    try:
        intentos["soft_psm6"] = _tess(_preproc_soft(bgr), 6)
    except Exception as exc:
        intentos["soft_psm6"] = ""
    try:
        intentos["binary_psm6"] = _tess(_preproc_binary(bgr), 6)
    except Exception:
        intentos["binary_psm6"] = ""
    try:
        intentos["binary_psm4"] = _tess(_preproc_binary(bgr), 4)
    except Exception:
        intentos["binary_psm4"] = ""
    try:
        intentos["deskew_psm6"] = _tess(_preproc_deskew(bgr), 6)
    except Exception:
        intentos["deskew_psm6"] = ""

    if not any(intentos.values()):
        return "", {"intentos": {k: 0 for k in intentos}}

    ganador = max(intentos.items(), key=lambda kv: len(kv[1] or ""))
    meta = {
        "ganador": ganador[0],
        "intentos": {k: len(v) for k, v in intentos.items()},
    }
    return ganador[1], meta
