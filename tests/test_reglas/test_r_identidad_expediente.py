"""
Tests R-IDENTIDAD-EXPEDIENTE — cubre cada fila de la tabla de Fase 1.

Aplica el ajuste obligatorio: BAJA_CONFIANZA / conf<umbral → REVISAR.
"""

from __future__ import annotations

from auditoria.config import UMBRAL_CONFIANZA_IDENTIDAD
from auditoria.reglas.r_identidad_expediente import REGLA_ID, evaluar
from modelo.decision_engine_output import (
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_EXPEDIENTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
    SEVERIDAD_MEDIA,
)


def _exp(estado: str, coincide: bool, conf: float, carpeta: str = "EXP-1") -> dict:
    return {
        "expediente_id_carpeta": carpeta,
        "resolucion_id": {
            "estado_resolucion": estado,
            "coincide_con_carpeta": coincide,
            "confianza_expediente": conf,
            "expediente_id_carpeta": carpeta,
            "expediente_id_detectado": carpeta if coincide else "EXP-OTRO",
        },
    }


def test_ok_alta_confianza():
    regla, hall = evaluar(_exp("OK", True, 0.95))
    assert regla.resultado == RESULTADO_OK
    assert regla.severidad is None
    assert regla.scope == SCOPE_EXPEDIENTE
    assert regla.regla_id == REGLA_ID
    assert hall == []


def test_ok_pero_conf_bajo_umbral_es_revisar_baja():
    """Ajuste 1: conf<umbral con resto OK → REVISAR (no OBSERVAR), severidad BAJA."""
    regla, hall = evaluar(_exp("OK", True, UMBRAL_CONFIANZA_IDENTIDAD - 0.05))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_BAJA
    assert len(hall) == 1
    assert hall[0].resultado == RESULTADO_REVISAR
    assert hall[0].severidad == SEVERIDAD_BAJA


def test_ok_pero_no_coincide_con_carpeta_es_revisar_alta():
    regla, hall = evaluar(_exp("OK", False, 0.99))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert len(hall) == 1


def test_baja_confianza_es_revisar_media():
    """Ajuste 1 obligatorio: BAJA_CONFIANZA → REVISAR, severidad MEDIA."""
    regla, hall = evaluar(_exp("BAJA_CONFIANZA", True, 0.7))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert len(hall) == 1


def test_baja_confianza_y_no_coincide_sigue_revisar():
    regla, hall = evaluar(_exp("BAJA_CONFIANZA", False, 0.5))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert len(hall) == 1


def test_conflicto_expediente_es_revisar_alta():
    regla, hall = evaluar(_exp("CONFLICTO_EXPEDIENTE", True, 0.6))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA


def test_estado_vacio_es_revisar_alta():
    regla, hall = evaluar(_exp("", False, 0.0))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA


def test_evidencia_consultada_completa():
    regla, _ = evaluar(_exp("OK", True, 0.95, carpeta="EXP-X"))
    ev = regla.evidencia_consultada
    assert ev["resolucion_id.estado_resolucion"] == "OK"
    assert ev["resolucion_id.coincide_con_carpeta"] is True
    assert ev["resolucion_id.confianza_expediente"] == 0.95
    assert ev["resolucion_id.expediente_id_carpeta"] == "EXP-X"


def test_3_criterios_emitidos():
    regla, _ = evaluar(_exp("OK", True, 0.95))
    assert len(regla.criterios_evaluados) == 3
    nombres = [c.criterio for c in regla.criterios_evaluados]
    assert any("estado_resolucion" in n for n in nombres)
    assert any("coincide_con_carpeta" in n for n in nombres)
    assert any("confianza_expediente" in n for n in nombres)
