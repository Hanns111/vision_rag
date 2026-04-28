"""
R-CAMPO-CRITICO-NULL — campos faltantes en cada comprobante.

Mapeo (ajuste obligatorio Fase 1: campo faltante = falta de evidencia):
  monto_total  null → REVISAR severidad=ALTA   (sin importe no hay validación de gasto)
  ruc          null → REVISAR severidad=ALTA   (identidad emisor)
  fecha        null → REVISAR severidad=MEDIA  (trazabilidad temporal)
  serie_numero null → REVISAR severidad=MEDIA  (identificación del comprobante)

`ruc_receptor` se evalúa en R-UE-RECEPTOR.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_scripts = str(Path(__file__).resolve().parent.parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from auditoria.reglas import peor  # noqa: E402
from modelo.decision_engine_output import (  # noqa: E402
    Hallazgo,
    ResultadoRegla,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


REGLA_ID = "R-CAMPO-CRITICO-NULL"
REGLA_VERSION = "v1.0"
DESCRIPCION = "Detección de campos críticos vacíos por comprobante"


_CAMPOS_CRITICOS: dict[str, tuple[str, str | None]] = {
    "monto_total": (RESULTADO_REVISAR, SEVERIDAD_ALTA),
    "ruc": (RESULTADO_REVISAR, SEVERIDAD_ALTA),
    "fecha": (RESULTADO_REVISAR, SEVERIDAD_MEDIA),
    "serie_numero": (RESULTADO_REVISAR, SEVERIDAD_MEDIA),
}


def _objeto_id(c: dict[str, Any]) -> str:
    return f"{c.get('archivo', '')}:{c.get('pagina_inicio', 0)}-{c.get('pagina_fin', 0)}"


def _es_null(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def evaluar(expediente: dict[str, Any]) -> tuple[ResultadoRegla, list[Hallazgo]]:
    comprobantes = expediente.get("comprobantes") or []
    expediente_id = expediente.get("expediente_id_carpeta") or ""

    hallazgos: list[Hallazgo] = []
    agregado: tuple[str, str | None] = (RESULTADO_OK, None)
    n_comp_con_null = 0
    n_nulls_total = 0

    for c in comprobantes:
        nulls_de_este = []
        for campo, (resultado, severidad) in _CAMPOS_CRITICOS.items():
            if _es_null(c.get(campo)):
                nulls_de_este.append((campo, resultado, severidad))
                agregado = peor(agregado, (resultado, severidad))

        if not nulls_de_este:
            continue

        n_comp_con_null += 1
        n_nulls_total += len(nulls_de_este)
        for campo, resultado, severidad in nulls_de_este:
            hallazgos.append(
                Hallazgo(
                    regla_id=REGLA_ID,
                    resultado=resultado,
                    severidad=severidad,
                    scope=SCOPE_COMPROBANTE,
                    objeto_id=_objeto_id(c),
                    explicacion=f"campo crítico vacío: {campo}",
                    campos_implicados=[campo],
                )
            )

    resultado_regla, severidad_regla = agregado
    explicacion = (
        f"Evaluados {len(comprobantes)} comprobantes; "
        f"{n_comp_con_null} con al menos un campo crítico vacío "
        f"({n_nulls_total} hallazgos individuales)."
    )

    regla = ResultadoRegla(
        regla_id=REGLA_ID,
        regla_version=REGLA_VERSION,
        descripcion_corta=DESCRIPCION,
        scope=SCOPE_COMPROBANTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=resultado_regla,
        severidad=severidad_regla,
        objeto_evaluado_id=expediente_id,
        evidencia_consultada={
            "n_comprobantes": len(comprobantes),
            "n_comprobantes_con_null_critico": n_comp_con_null,
            "n_hallazgos": n_nulls_total,
            "campos_evaluados": list(_CAMPOS_CRITICOS.keys()),
        },
        criterios_evaluados=[],
        explicacion=explicacion,
        campos_implicados=[f"comprobantes[].{k}" for k in _CAMPOS_CRITICOS],
    )
    return regla, hallazgos
