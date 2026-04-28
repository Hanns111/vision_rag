"""
R-CONSISTENCIA — passthrough auditable del `estado_consistencia` por comprobante.

Lee `comprobantes[].{estado_consistencia, tipo_tributario, detalle_inconsistencia}`
ya calculados por el consolidador (D-19 + PRE-PASO 4.5 / D-24). El motor solo
eleva la observación a decisión: no recomputa montos.

Mapeo (ajustes obligatorios Fase 1):
  OK                  → OK
  DIFERENCIA_LEVE     → OBSERVAR severidad=BAJA
  DIFERENCIA_CRITICA  → OBSERVAR severidad=ALTA
  DATOS_INSUFICIENTES → REVISAR  severidad=MEDIA
  ""  (no calculado)  → REVISAR  severidad=ALTA  (defensivo: input no es v4)

Principio: OBSERVAR = incumplimiento numérico verificable;
REVISAR = evidencia insuficiente para verificar.
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
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
    SEVERIDAD_MEDIA,
)


REGLA_ID = "R-CONSISTENCIA"
REGLA_VERSION = "v1.0"
DESCRIPCION = "Consistencia tributaria por comprobante (passthrough del consolidador)"


_MAPEO: dict[str, tuple[str, str | None]] = {
    "OK": (RESULTADO_OK, None),
    "DIFERENCIA_LEVE": (RESULTADO_OBSERVAR, SEVERIDAD_BAJA),
    "DIFERENCIA_CRITICA": (RESULTADO_OBSERVAR, SEVERIDAD_ALTA),
    "DATOS_INSUFICIENTES": (RESULTADO_REVISAR, SEVERIDAD_MEDIA),
    "": (RESULTADO_REVISAR, SEVERIDAD_ALTA),
}


def _objeto_id(c: dict[str, Any]) -> str:
    return f"{c.get('archivo', '')}:{c.get('pagina_inicio', 0)}-{c.get('pagina_fin', 0)}"


def evaluar(expediente: dict[str, Any]) -> tuple[ResultadoRegla, list[Hallazgo]]:
    comprobantes = expediente.get("comprobantes") or []
    expediente_id = expediente.get("expediente_id_carpeta") or ""

    hallazgos: list[Hallazgo] = []
    agregado: tuple[str, str | None] = (RESULTADO_OK, None)
    contadores = {"OK": 0, "OBSERVAR": 0, "REVISAR": 0}

    for c in comprobantes:
        estado = c.get("estado_consistencia") or ""
        resultado, severidad = _MAPEO.get(estado, (RESULTADO_REVISAR, SEVERIDAD_ALTA))
        contadores[resultado] = contadores.get(resultado, 0) + 1
        agregado = peor(agregado, (resultado, severidad))

        if resultado == RESULTADO_OK:
            continue

        detalle = c.get("detalle_inconsistencia") or ""
        tipo = c.get("tipo_tributario") or ""
        expl = (
            f"estado_consistencia={estado!r}, tipo_tributario={tipo!r}"
            + (f"; detalle={detalle}" if detalle else "")
        )
        hallazgos.append(
            Hallazgo(
                regla_id=REGLA_ID,
                resultado=resultado,
                severidad=severidad,
                scope=SCOPE_COMPROBANTE,
                objeto_id=_objeto_id(c),
                explicacion=expl,
                campos_implicados=[
                    "estado_consistencia",
                    "tipo_tributario",
                    "detalle_inconsistencia",
                ],
            )
        )

    resultado_regla, severidad_regla = agregado
    n_total = len(comprobantes)
    explicacion = (
        f"Evaluados {n_total} comprobantes — OK={contadores['OK']}, "
        f"OBSERVAR={contadores['OBSERVAR']}, REVISAR={contadores['REVISAR']}."
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
            "n_comprobantes": n_total,
            "n_ok": contadores["OK"],
            "n_observar": contadores["OBSERVAR"],
            "n_revisar": contadores["REVISAR"],
        },
        criterios_evaluados=[],
        explicacion=explicacion,
        campos_implicados=[
            "comprobantes[].estado_consistencia",
            "comprobantes[].tipo_tributario",
            "comprobantes[].detalle_inconsistencia",
        ],
    )
    return regla, hallazgos
