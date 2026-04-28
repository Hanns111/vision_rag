"""
R-UE-RECEPTOR — coherencia del receptor del comprobante con la UE esperada.

Mapeo (ajuste obligatorio Fase 1):
  ruc_receptor presente y == UE_ESPERADA → OK
  ruc_receptor presente y != UE_ESPERADA → OBSERVAR severidad=ALTA
                                            (incumplimiento verificable: receptor incorrecto)
  ruc_receptor ausente / null            → REVISAR  severidad=MEDIA
                                            (falta de evidencia)

`UE_ESPERADA` proviene de `auditoria.config` y es **valor temporal del MVP**:
hardcodeado al RUC de MINEDU para el corpus piloto. En fase posterior debe
derivarse del propio expediente.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_scripts = str(Path(__file__).resolve().parent.parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from auditoria.config import UE_ESPERADA  # noqa: E402
from auditoria.reglas import peor  # noqa: E402
from modelo.decision_engine_output import (  # noqa: E402
    Hallazgo,
    ResultadoRegla,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


REGLA_ID = "R-UE-RECEPTOR"
REGLA_VERSION = "v1.0"
DESCRIPCION = "Coherencia del RUC receptor con la UE esperada (MVP: valor configurado)"


def _objeto_id(c: dict[str, Any]) -> str:
    return f"{c.get('archivo', '')}:{c.get('pagina_inicio', 0)}-{c.get('pagina_fin', 0)}"


def evaluar(expediente: dict[str, Any]) -> tuple[ResultadoRegla, list[Hallazgo]]:
    comprobantes = expediente.get("comprobantes") or []
    expediente_id = expediente.get("expediente_id_carpeta") or ""

    hallazgos: list[Hallazgo] = []
    agregado: tuple[str, str | None] = (RESULTADO_OK, None)
    n_ok = 0
    n_distinto = 0
    n_ausente = 0

    for c in comprobantes:
        rr = c.get("ruc_receptor")
        if rr is None or (isinstance(rr, str) and rr.strip() == ""):
            n_ausente += 1
            resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_MEDIA
            agregado = peor(agregado, (resultado, severidad))
            hallazgos.append(
                Hallazgo(
                    regla_id=REGLA_ID,
                    resultado=resultado,
                    severidad=severidad,
                    scope=SCOPE_COMPROBANTE,
                    objeto_id=_objeto_id(c),
                    explicacion="ruc_receptor ausente; no se puede verificar UE.",
                    campos_implicados=["ruc_receptor"],
                )
            )
            continue
        if rr == UE_ESPERADA:
            n_ok += 1
            continue
        n_distinto += 1
        resultado, severidad = RESULTADO_OBSERVAR, SEVERIDAD_ALTA
        agregado = peor(agregado, (resultado, severidad))
        hallazgos.append(
            Hallazgo(
                regla_id=REGLA_ID,
                resultado=resultado,
                severidad=severidad,
                scope=SCOPE_COMPROBANTE,
                objeto_id=_objeto_id(c),
                explicacion=(
                    f"ruc_receptor={rr!r} ≠ UE_ESPERADA={UE_ESPERADA!r} "
                    f"(MVP: configuración temporal)."
                ),
                campos_implicados=["ruc_receptor"],
            )
        )

    resultado_regla, severidad_regla = agregado
    explicacion = (
        f"Evaluados {len(comprobantes)} comprobantes contra UE_ESPERADA={UE_ESPERADA!r}: "
        f"OK={n_ok}, receptor_distinto={n_distinto}, ausentes={n_ausente}."
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
            "ue_esperada_mvp": UE_ESPERADA,
            "n_comprobantes": len(comprobantes),
            "n_receptor_ok": n_ok,
            "n_receptor_distinto": n_distinto,
            "n_receptor_ausente": n_ausente,
        },
        criterios_evaluados=[],
        explicacion=explicacion,
        campos_implicados=["comprobantes[].ruc_receptor"],
    )
    return regla, hallazgos
