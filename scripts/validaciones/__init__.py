"""
Validaciones normativas sobre expedientes (control previo).

Cada validación:
  - recibe solo texto (desacoplada de OCR/Excel),
  - devuelve un dataclass con estado, errores, confianza y evidencia,
  - es determinista y auditable (sin LLM en este paso).
"""

from __future__ import annotations

__all__ = ["firmas_anexo3"]
