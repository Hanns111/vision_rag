"""
Tests R-FIRMAS — solo contra valores REALES descubiertos en el código y JSONs:

  CONFORME              → OK
  OBSERVADO             → OBSERVAR severidad=ALTA
  INSUFICIENTE_EVIDENCIA → REVISAR  severidad=MEDIA
  (sin firmas_anexo3)   → NO_APLICABLE
"""

from __future__ import annotations

from auditoria.reglas.r_firmas import REGLA_ID, TIPO_VALIDACION, evaluar
from modelo.decision_engine_output import (
    RESULTADO_NO_APLICABLE,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCOPE_EXPEDIENTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_MEDIA,
)


def _exp(*validaciones) -> dict:
    return {
        "expediente_id_carpeta": "EXP-1",
        "validaciones": list(validaciones),
    }


def _val(estado: str, errores=None, conf=0.5) -> dict:
    return {
        "tipo_validacion": TIPO_VALIDACION,
        "estado": estado,
        "errores": errores or [],
        "confianza": conf,
    }


def test_conforme_es_ok():
    regla, hall = evaluar(_exp(_val("CONFORME", conf=0.9)))
    assert regla.resultado == RESULTADO_OK
    assert regla.severidad is None
    assert regla.regla_id == REGLA_ID
    assert regla.scope == SCOPE_EXPEDIENTE
    assert hall == []


def test_observado_es_observar_alta():
    """Valor real más común en corpus actual (3/4 documentos)."""
    regla, hall = evaluar(_exp(_val("OBSERVADO", errores=["rol_no_detectado:jefe_unidad"])))
    assert regla.resultado == RESULTADO_OBSERVAR
    assert regla.severidad == SEVERIDAD_ALTA
    assert len(hall) == 1
    assert "OBSERVADO" in hall[0].explicacion


def test_insuficiente_evidencia_es_revisar_media():
    regla, hall = evaluar(_exp(_val("INSUFICIENTE_EVIDENCIA")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    assert len(hall) == 1


def test_sin_firmas_anexo3_es_no_aplicable():
    regla, hall = evaluar(_exp())
    assert regla.resultado == RESULTADO_NO_APLICABLE
    assert regla.severidad is None
    assert hall == []
    assert regla.evidencia_consultada["validaciones_firmas_anexo3"] == 0


def test_validacion_no_firmas_se_ignora():
    """Solo cuentan entries con tipo_validacion=='firmas_anexo3'."""
    otra = {"tipo_validacion": "monto_maximo", "estado": "CONFORME"}
    regla, _ = evaluar(_exp(otra))
    assert regla.resultado == RESULTADO_NO_APLICABLE


def test_estado_desconocido_cae_a_revisar_alta_defensivo():
    """Si aparece un estado fuera de los 3 reales, defensivo → REVISAR ALTA."""
    regla, hall = evaluar(_exp(_val("INVENTADO_NO_EXISTE")))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_ALTA


def test_multiples_firmas_toma_peor_estado():
    regla, hall = evaluar(_exp(
        _val("CONFORME"),
        _val("OBSERVADO"),
        _val("INSUFICIENTE_EVIDENCIA"),
    ))
    assert regla.resultado == RESULTADO_REVISAR
    assert regla.severidad == SEVERIDAD_MEDIA
    # 2 hallazgos (OBSERVADO + INSUFICIENTE), CONFORME no genera.
    assert len(hall) == 2
