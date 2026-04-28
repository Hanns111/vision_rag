"""
R-FIRMAS — verificación normativa de firmas de Anexo 3 (planilla del expediente).

Lee `validaciones[]` del expediente.json filtrando entradas con
`tipo_validacion == "firmas_anexo3"`.

Mapeo (ajuste obligatorio Fase 1, contra valores REALES descubiertos en
`scripts/validaciones/firmas_anexo3.py:29-31` y JSONs reales):
  CONFORME              → OK
  OBSERVADO             → OBSERVAR severidad=ALTA
  INSUFICIENTE_EVIDENCIA → REVISAR  severidad=MEDIA
  (sin entrada de firmas_anexo3) → NO_APLICABLE
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
    RESULTADO_NO_APLICABLE,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_EXPEDIENTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


REGLA_ID = "R-FIRMAS"
REGLA_VERSION = "v1.0"
DESCRIPCION = "Validación normativa de firmas en Anexo 3 (planilla)"

TIPO_VALIDACION = "firmas_anexo3"


_MAPEO: dict[str, tuple[str, str | None]] = {
    "CONFORME": (RESULTADO_OK, None),
    "OBSERVADO": (RESULTADO_OBSERVAR, SEVERIDAD_ALTA),
    "INSUFICIENTE_EVIDENCIA": (RESULTADO_REVISAR, SEVERIDAD_MEDIA),
}


def evaluar(expediente: dict[str, Any]) -> tuple[ResultadoRegla, list[Hallazgo]]:
    expediente_id = expediente.get("expediente_id_carpeta") or ""
    validaciones = expediente.get("validaciones") or []
    firmas = [
        v for v in validaciones
        if isinstance(v, dict) and v.get("tipo_validacion") == TIPO_VALIDACION
    ]

    if not firmas:
        regla = ResultadoRegla(
            regla_id=REGLA_ID,
            regla_version=REGLA_VERSION,
            descripcion_corta=DESCRIPCION,
            scope=SCOPE_EXPEDIENTE,
            severidad_max=SEVERIDAD_ALTA,
            resultado=RESULTADO_NO_APLICABLE,
            severidad=None,
            objeto_evaluado_id=expediente_id,
            evidencia_consultada={"validaciones_firmas_anexo3": 0},
            criterios_evaluados=[],
            explicacion="No se encontró validación firmas_anexo3 en el expediente.",
            campos_implicados=["validaciones[].tipo_validacion", "validaciones[].estado"],
        )
        return regla, []

    hallazgos: list[Hallazgo] = []
    agregado: tuple[str, str | None] = (RESULTADO_OK, None)
    estados_observados: list[str] = []

    for v in firmas:
        estado = v.get("estado") or ""
        estados_observados.append(estado)
        resultado, severidad = _MAPEO.get(estado, (RESULTADO_REVISAR, SEVERIDAD_ALTA))
        agregado = peor(agregado, (resultado, severidad))

        if resultado == RESULTADO_OK:
            continue

        errores = v.get("errores") or []
        confianza = v.get("confianza")
        expl = (
            f"firmas_anexo3.estado={estado!r}, confianza={confianza}, "
            f"errores={errores!r}"
        )
        hallazgos.append(
            Hallazgo(
                regla_id=REGLA_ID,
                resultado=resultado,
                severidad=severidad,
                scope=SCOPE_EXPEDIENTE,
                objeto_id=expediente_id,
                explicacion=expl,
                campos_implicados=[
                    "validaciones[].estado",
                    "validaciones[].errores",
                    "validaciones[].confianza",
                ],
            )
        )

    resultado_regla, severidad_regla = agregado
    explicacion = (
        f"{len(firmas)} validación(es) firmas_anexo3 evaluadas — "
        f"estados observados: {estados_observados}."
    )

    regla = ResultadoRegla(
        regla_id=REGLA_ID,
        regla_version=REGLA_VERSION,
        descripcion_corta=DESCRIPCION,
        scope=SCOPE_EXPEDIENTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=resultado_regla,
        severidad=severidad_regla,
        objeto_evaluado_id=expediente_id,
        evidencia_consultada={
            "validaciones_firmas_anexo3": len(firmas),
            "estados_observados": estados_observados,
        },
        criterios_evaluados=[],
        explicacion=explicacion,
        campos_implicados=[
            "validaciones[].tipo_validacion",
            "validaciones[].estado",
        ],
    )
    return regla, hallazgos
