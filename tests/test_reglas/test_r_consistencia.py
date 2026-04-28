"""
Tests R-CONSISTENCIA — un caso por fila de la tabla de mapeo + agregación.

Mapeo verificado:
  OK                  → OK
  DIFERENCIA_LEVE     → OBSERVAR severidad=BAJA
  DIFERENCIA_CRITICA  → OBSERVAR severidad=ALTA
  DATOS_INSUFICIENTES → REVISAR  severidad=MEDIA
  ""                  → REVISAR  severidad=ALTA
"""

from __future__ import annotations

from auditoria.reglas.r_consistencia import REGLA_ID, evaluar
from modelo.decision_engine_output import (
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
    SEVERIDAD_MEDIA,
)


def _comp(estado: str, archivo="d.pdf", pi=1, pf=1, tipo="GRAVADA", detalle="") -> dict:
    return {
        "archivo": archivo,
        "pagina_inicio": pi,
        "pagina_fin": pf,
        "estado_consistencia": estado,
        "tipo_tributario": tipo,
        "detalle_inconsistencia": detalle,
    }


def _exp(*comprobantes) -> dict:
    return {"expediente_id_carpeta": "EXP-1", "comprobantes": list(comprobantes)}


def test_solo_ok():
    regla, hall = evaluar(_exp(_comp("OK"), _comp("OK", pi=2, pf=2)))
    assert regla.resultado == RESULTADO_OK
    assert regla.severidad is None
    assert regla.regla_id == REGLA_ID
    assert regla.scope == SCOPE_COMPROBANTE
    assert hall == []


def test_diferencia_leve_es_observar_baja():
    regla, hall = evaluar(_exp(_comp("DIFERENCIA_LEVE")))
    assert regla.resultado == RESULTADO_OBSERVAR
    assert regla.severidad == SEVERIDAD_BAJA
    assert len(hall) == 1
    assert hall[0].resultado == RESULTADO_OBSERVAR
    assert hall[0].severidad == SEVERIDAD_BAJA


def test_diferencia_critica_es_observar_alta():
    regla, hall = evaluar(_exp(_comp("DIFERENCIA_CRITICA")))
    assert regla.resultado == RESULTADO_OBSERVAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert hall[0].severidad == SEVERIDAD_ALTA


def test_datos_insuficientes_es_revisar_media():
    regla, hall = evaluar(_exp(_comp("DATOS_INSUFICIENTES")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA


def test_estado_vacio_es_revisar_alta():
    """Defensivo: input pre-v4 → REVISAR ALTA."""
    regla, hall = evaluar(_exp(_comp("")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA


def test_agregacion_peor_severidad_gana():
    """Mezcla OK + LEVE + CRITICA + INSUFICIENTES → REVISAR domina."""
    regla, hall = evaluar(_exp(
        _comp("OK", pi=1, pf=1),
        _comp("DIFERENCIA_LEVE", pi=2, pf=2),
        _comp("DIFERENCIA_CRITICA", pi=3, pf=3),
        _comp("DATOS_INSUFICIENTES", pi=4, pf=4),
    ))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    # Solo 3 hallazgos (el OK no genera).
    assert len(hall) == 3


def test_evidencia_consultada_cuenta_correctamente():
    regla, _ = evaluar(_exp(
        _comp("OK"),
        _comp("DIFERENCIA_LEVE", pi=2, pf=2),
        _comp("DATOS_INSUFICIENTES", pi=3, pf=3),
    ))
    ev = regla.evidencia_consultada
    assert ev["n_comprobantes"] == 3
    assert ev["n_ok"] == 1
    assert ev["n_observar"] == 1
    assert ev["n_revisar"] == 1


def test_objeto_id_combina_archivo_y_paginas():
    regla, hall = evaluar(_exp(_comp("DIFERENCIA_LEVE", archivo="x.pdf", pi=5, pf=7)))
    assert hall[0].objeto_id == "x.pdf:5-7"
