"""
Tests R-UE-RECEPTOR — coherencia receptor vs UE configurada.

Mapeo verificado:
  ruc_receptor == UE_ESPERADA      → OK
  ruc_receptor != UE_ESPERADA      → OBSERVAR severidad=ALTA
  ruc_receptor null/vacío          → REVISAR  severidad=MEDIA
"""

from __future__ import annotations

from auditoria.config import UE_ESPERADA
from auditoria.reglas.r_ue_receptor import REGLA_ID, evaluar
from modelo.decision_engine_output import (
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_COMPROBANTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


def _comp(ruc_receptor, archivo="d.pdf", pi=1, pf=1) -> dict:
    return {
        "archivo": archivo,
        "pagina_inicio": pi,
        "pagina_fin": pf,
        "ruc_receptor": ruc_receptor,
    }


def _exp(*comprobantes) -> dict:
    return {"expediente_id_carpeta": "EXP-1", "comprobantes": list(comprobantes)}


def test_receptor_coincide_con_ue_es_ok():
    regla, hall = evaluar(_exp(_comp(UE_ESPERADA), _comp(UE_ESPERADA, pi=2, pf=2)))
    assert regla.resultado == RESULTADO_OK
    assert regla.severidad is None
    assert regla.regla_id == REGLA_ID
    assert regla.scope == SCOPE_COMPROBANTE
    assert hall == []


def test_receptor_distinto_es_observar_alta():
    """Incumplimiento verificable: receptor no es la UE configurada."""
    regla, hall = evaluar(_exp(_comp("99999999999")))
    assert regla.resultado == RESULTADO_OBSERVAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert len(hall) == 1
    assert hall[0].severidad == SEVERIDAD_ALTA


def test_receptor_ausente_es_revisar_media():
    """Falta de evidencia: no se puede verificar la UE."""
    regla, hall = evaluar(_exp(_comp(None)))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert len(hall) == 1


def test_receptor_string_vacio_es_ausente():
    regla, _ = evaluar(_exp(_comp("")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA


def test_mezcla_ok_distinto_ausente_agrega_a_revisar():
    """Cualquier REVISAR domina sobre OBSERVAR."""
    regla, hall = evaluar(_exp(
        _comp(UE_ESPERADA, pi=1, pf=1),
        _comp("99999999999", pi=2, pf=2),
        _comp(None, pi=3, pf=3),
    ))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert len(hall) == 2  # solo el distinto y el ausente generan hallazgo


def test_evidencia_consultada_contadores():
    regla, _ = evaluar(_exp(
        _comp(UE_ESPERADA),
        _comp("11111111111", pi=2, pf=2),
        _comp(None, pi=3, pf=3),
        _comp(None, pi=4, pf=4),
    ))
    ev = regla.evidencia_consultada
    assert ev["ue_esperada_mvp"] == UE_ESPERADA
    assert ev["n_comprobantes"] == 4
    assert ev["n_receptor_ok"] == 1
    assert ev["n_receptor_distinto"] == 1
    assert ev["n_receptor_ausente"] == 2


def test_expediente_sin_comprobantes_es_ok():
    """Sin comprobantes a evaluar, no hay incumplimiento ni evidencia faltante."""
    regla, hall = evaluar(_exp())
    assert regla.resultado == RESULTADO_OK
    assert hall == []
