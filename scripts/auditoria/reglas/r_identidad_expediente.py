"""
R-IDENTIDAD-EXPEDIENTE — coherencia de identidad detectada vs carpeta.

Lee `resolucion_id.{estado_resolucion, coincide_con_carpeta, confianza_expediente,
expediente_id_carpeta, expediente_id_detectado}` y emite un único veredicto.

Ajuste obligatorio Fase 1: BAJA_CONFIANZA y/o conf < umbral → REVISAR
(falta de certeza, no incumplimiento).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_scripts = str(Path(__file__).resolve().parent.parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from auditoria.config import UMBRAL_CONFIANZA_IDENTIDAD  # noqa: E402
from modelo.decision_engine_output import (  # noqa: E402
    Criterio,
    Hallazgo,
    ResultadoRegla,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_EXPEDIENTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
    SEVERIDAD_MEDIA,
)


REGLA_ID = "R-IDENTIDAD-EXPEDIENTE"
REGLA_VERSION = "v1.0"
DESCRIPCION = "Coherencia entre identidad administrativa detectada y carpeta del expediente"


def evaluar(expediente: dict[str, Any]) -> tuple[ResultadoRegla, list[Hallazgo]]:
    res = expediente.get("resolucion_id") or {}
    estado = res.get("estado_resolucion") or ""
    coincide = bool(res.get("coincide_con_carpeta"))
    conf_raw = res.get("confianza_expediente")
    conf = float(conf_raw) if conf_raw is not None else 0.0
    carpeta = (
        res.get("expediente_id_carpeta")
        or expediente.get("expediente_id_carpeta")
        or ""
    )
    detectado = res.get("expediente_id_detectado") or ""

    evidencia: dict[str, Any] = {
        "resolucion_id.estado_resolucion": estado,
        "resolucion_id.coincide_con_carpeta": coincide,
        "resolucion_id.confianza_expediente": round(conf, 3),
        "resolucion_id.expediente_id_carpeta": carpeta,
        "resolucion_id.expediente_id_detectado": detectado,
    }
    campos_imp = [
        "resolucion_id.estado_resolucion",
        "resolucion_id.coincide_con_carpeta",
        "resolucion_id.confianza_expediente",
    ]

    if estado == "OK" and coincide and conf >= UMBRAL_CONFIANZA_IDENTIDAD:
        resultado, severidad = RESULTADO_OK, None
        explicacion = (
            f"Identidad detectada {detectado!r} coincide con carpeta {carpeta!r} "
            f"(confianza={conf:.3f} ≥ umbral={UMBRAL_CONFIANZA_IDENTIDAD})."
        )
    elif estado == "OK" and coincide and conf < UMBRAL_CONFIANZA_IDENTIDAD:
        resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_BAJA
        explicacion = (
            f"Identidad coincide con carpeta pero confianza={conf:.3f} < "
            f"umbral={UMBRAL_CONFIANZA_IDENTIDAD}: falta certeza para certificar."
        )
    elif estado == "OK" and not coincide:
        resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_ALTA
        explicacion = (
            f"Identidad detectada {detectado!r} no coincide con carpeta {carpeta!r}."
        )
    elif estado == "BAJA_CONFIANZA":
        resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_MEDIA
        explicacion = (
            f"Resolución reportó BAJA_CONFIANZA (confianza={conf:.3f}, "
            f"coincide_con_carpeta={coincide}): falta certeza."
        )
    elif estado == "CONFLICTO_EXPEDIENTE":
        resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_ALTA
        explicacion = "Conflicto entre múltiples identidades candidatas detectadas en el expediente."
    else:
        resultado, severidad = RESULTADO_REVISAR, SEVERIDAD_ALTA
        explicacion = (
            f"Estado de resolución {estado!r} no certifica identidad."
        )

    criterios = [
        Criterio(
            criterio="estado_resolucion == 'OK'",
            valor=estado,
            ok=(estado == "OK"),
        ),
        Criterio(
            criterio="coincide_con_carpeta is True",
            valor=coincide,
            ok=coincide,
        ),
        Criterio(
            criterio=f"confianza_expediente >= {UMBRAL_CONFIANZA_IDENTIDAD}",
            valor=round(conf, 3),
            ok=(conf >= UMBRAL_CONFIANZA_IDENTIDAD),
        ),
    ]

    regla = ResultadoRegla(
        regla_id=REGLA_ID,
        regla_version=REGLA_VERSION,
        descripcion_corta=DESCRIPCION,
        scope=SCOPE_EXPEDIENTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=resultado,
        severidad=severidad,
        objeto_evaluado_id=carpeta or expediente.get("expediente_id_carpeta") or "",
        evidencia_consultada=evidencia,
        criterios_evaluados=criterios,
        explicacion=explicacion,
        campos_implicados=campos_imp,
    )

    hallazgos: list[Hallazgo] = []
    if resultado != RESULTADO_OK:
        hallazgos.append(
            Hallazgo(
                regla_id=REGLA_ID,
                resultado=resultado,
                severidad=severidad,
                scope=SCOPE_EXPEDIENTE,
                objeto_id=carpeta or "",
                explicacion=explicacion,
                campos_implicados=campos_imp,
            )
        )
    return regla, hallazgos
