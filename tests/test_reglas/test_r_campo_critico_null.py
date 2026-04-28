"""
Tests R-CAMPO-CRITICO-NULL — todos los campos null mapean a REVISAR.

Severidades:
  monto_total / ruc           → ALTA
  fecha / serie_numero        → MEDIA
"""

from __future__ import annotations

from auditoria.reglas.r_campo_critico_null import REGLA_ID, evaluar
from modelo.decision_engine_output import (
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


def _comp(**campos) -> dict:
    base = {
        "archivo": "d.pdf",
        "pagina_inicio": 1,
        "pagina_fin": 1,
        "monto_total": "100.00",
        "ruc": "20111111111",
        "fecha": "2026-04-15",
        "serie_numero": "F001-001",
    }
    base.update(campos)
    return base


def _exp(*comprobantes) -> dict:
    return {"expediente_id_carpeta": "EXP-1", "comprobantes": list(comprobantes)}


def test_todos_campos_presentes_es_ok():
    regla, hall = evaluar(_exp(_comp(), _comp(pagina_inicio=2, pagina_fin=2)))
    assert regla.resultado == RESULTADO_OK
    assert regla.severidad is None
    assert regla.regla_id == REGLA_ID
    assert regla.scope == SCOPE_COMPROBANTE
    assert hall == []


def test_monto_total_null_revisar_alta():
    regla, hall = evaluar(_exp(_comp(monto_total=None)))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert len(hall) == 1
    assert hall[0].campos_implicados == ["monto_total"]
    assert hall[0].severidad == SEVERIDAD_ALTA


def test_ruc_null_revisar_alta():
    regla, hall = evaluar(_exp(_comp(ruc=None)))
    assert regla.severidad == SEVERIDAD_ALTA
    assert hall[0].campos_implicados == ["ruc"]


def test_fecha_null_revisar_media():
    regla, hall = evaluar(_exp(_comp(fecha=None)))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert hall[0].campos_implicados == ["fecha"]


def test_serie_numero_vacio_string_es_null():
    regla, hall = evaluar(_exp(_comp(serie_numero="")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA


def test_un_comprobante_con_dos_nulls_genera_dos_hallazgos():
    regla, hall = evaluar(_exp(_comp(monto_total=None, fecha=None)))
    assert len(hall) == 2
    campos = sorted(h.campos_implicados[0] for h in hall)
    assert campos == ["fecha", "monto_total"]
    # Severidad agregada = la peor (ALTA por monto_total).
    assert regla.severidad == SEVERIDAD_ALTA


def test_agregacion_max_severidad_entre_comprobantes():
    """Comp1 fecha-null (MEDIA), Comp2 ruc-null (ALTA) → severidad ALTA."""
    regla, hall = evaluar(_exp(
        _comp(fecha=None),
        _comp(ruc=None, pagina_inicio=2, pagina_fin=2),
    ))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert len(hall) == 2


def test_evidencia_consultada_contadores():
    regla, _ = evaluar(_exp(
        _comp(),                                  # 0 nulls
        _comp(monto_total=None, pagina_inicio=2, pagina_fin=2),  # 1 null
    ))
    ev = regla.evidencia_consultada
    assert ev["n_comprobantes"] == 2
    assert ev["n_comprobantes_con_null_critico"] == 1
    assert ev["n_hallazgos"] == 1
    assert "monto_total" in ev["campos_evaluados"]
    # ruc_receptor NO se evalúa aquí (queda en R-UE-RECEPTOR).
    assert "ruc_receptor" not in ev["campos_evaluados"]
