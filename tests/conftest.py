"""
Configuración de pytest para el proyecto vision_rag.

Inserta `scripts/` en `sys.path` para que los tests puedan importar módulos
del proyecto (p. ej. `modelo.consistencia_tributaria`, `consolidador`) sin
reproducir el truco de inyección de path que hacen los CLIs en
`scripts/ingest_expedientes.py:21-23` y `scripts/consolidador.py:36-38`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
