"""
Ingesta de expedientes reales para validación humana asistida.

Alimenta el Excel `data/piloto_ocr/metrics/validacion_expedientes.xlsx`.
Flujo: scanner -> text_reader -> classifier -> extractor -> excel_export.
"""

from __future__ import annotations

__all__ = [
    "scanner",
    "text_reader",
    "classifier",
    "extractor",
    "excel_export",
]
