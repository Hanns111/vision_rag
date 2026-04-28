"""
Tests de las dataclasses del schema `decision_engine.v1` (Commit 1, Fase 1).

Solo verifica serialización determinista. Sin lógica de reglas (Commit 2)
ni orquestador (Commit 3). El módulo bajo test no importa nada del paquete
`auditoria/` para mantener la separación schema vs lógica.
"""

from __future__ import annotations

import json

from modelo.decision_engine_output import (
    Criterio,
    DecisionEngineOutput,
    Hallazgo,
    MetadataCorrida,
    ResultadoRegla,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCHEMA_VERSION,
    SCOPE_COMPROBANTE,
    SCOPE_EXPEDIENTE,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
)


def _build_output_minimo() -> DecisionEngineOutput:
    """Output sintético cubriendo: 1 regla OK + 1 regla con hallazgo OBSERVAR."""
    regla_ok = ResultadoRegla(
        regla_id="R-IDENTIDAD-EXPEDIENTE",
        regla_version="v1.0",
        descripcion_corta="Coherencia de identidad detectada vs carpeta",
        scope=SCOPE_EXPEDIENTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=RESULTADO_OK,
        severidad=None,
        objeto_evaluado_id="EXP-TEST-0001",
        evidencia_consultada={"resolucion_id.estado_resolucion": "OK"},
        criterios_evaluados=[
            Criterio(criterio="estado_resolucion == 'OK'", valor="OK", ok=True),
        ],
        explicacion="Identidad OK.",
        campos_implicados=["resolucion_id.estado_resolucion"],
    )
    regla_obs = ResultadoRegla(
        regla_id="R-CONSISTENCIA",
        regla_version="v1.0",
        descripcion_corta="Consistencia tributaria por comprobante",
        scope=SCOPE_COMPROBANTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=RESULTADO_OBSERVAR,
        severidad=SEVERIDAD_BAJA,
        objeto_evaluado_id="dummy.pdf:1-1",
        evidencia_consultada={"estado_consistencia": "DIFERENCIA_LEVE"},
        criterios_evaluados=[],
        explicacion="Diferencia leve detectada.",
        campos_implicados=["estado_consistencia"],
    )
    hall = Hallazgo(
        regla_id="R-CONSISTENCIA",
        resultado=RESULTADO_OBSERVAR,
        severidad=SEVERIDAD_BAJA,
        scope=SCOPE_COMPROBANTE,
        objeto_id="dummy.pdf:1-1",
        explicacion="Diferencia leve detectada.",
        campos_implicados=["estado_consistencia", "monto_total"],
    )
    md = MetadataCorrida(
        engine_run_id="run-test-1",
        engine_run_timestamp_utc="2026-04-28T00:00:00Z",
        engine_host="testhost",
        engine_git_commit="0000000",
    )
    return DecisionEngineOutput(
        expediente_id="EXP-TEST-0001",
        input_referenciado={
            "expediente_json_path": "tests/fixture/expediente.json",
            "expediente_json_sha256": "deadbeef",
            "expediente_schema_version": "expediente.v4",
        },
        decision_global=RESULTADO_OBSERVAR,
        resumen={
            "n_reglas_definidas": 2,
            "n_reglas_evaluadas": 2,
            "n_reglas_aplicables": 2,
            "por_severidad": {"OK": 1, "OBSERVAR": 1, "REVISAR": 0},
            "por_regla": {
                "R-IDENTIDAD-EXPEDIENTE": "OK",
                "R-CONSISTENCIA": "OBSERVAR",
            },
        },
        reglas_evaluadas=[regla_ok, regla_obs],
        hallazgos=[hall],
        metadata_corrida=md,
    )


def test_criterio_to_dict_orden_explicito():
    c = Criterio(criterio="x == 1", valor=1, ok=True)
    d = c.to_dict()
    assert list(d.keys()) == ["criterio", "valor", "ok"]
    assert d == {"criterio": "x == 1", "valor": 1, "ok": True}


def test_hallazgo_to_dict_con_severidad_y_sin():
    h_con = Hallazgo(
        regla_id="R-X",
        resultado=RESULTADO_REVISAR,
        severidad=SEVERIDAD_ALTA,
        scope=SCOPE_COMPROBANTE,
        objeto_id="a.pdf:1-1",
        explicacion="x",
        campos_implicados=["a", "b"],
    )
    d = h_con.to_dict()
    assert d["severidad"] == SEVERIDAD_ALTA
    assert d["campos_implicados"] == ["a", "b"]

    h_sin = Hallazgo(
        regla_id="R-Y",
        resultado=RESULTADO_OBSERVAR,
        severidad=None,
        scope=SCOPE_EXPEDIENTE,
        objeto_id="EXP-1",
        explicacion="y",
    )
    assert h_sin.to_dict()["severidad"] is None
    assert h_sin.to_dict()["campos_implicados"] == []


def test_resultadoregla_to_dict_estructura_completa():
    r = ResultadoRegla(
        regla_id="R-X",
        regla_version="v1.0",
        descripcion_corta="desc",
        scope=SCOPE_EXPEDIENTE,
        severidad_max=SEVERIDAD_ALTA,
        resultado=RESULTADO_OK,
        severidad=None,
        objeto_evaluado_id="EXP-1",
    )
    d = r.to_dict()
    esperadas = {
        "regla_id", "regla_version", "descripcion_corta", "scope",
        "severidad_max", "resultado", "severidad", "objeto_evaluado_id",
        "evidencia_consultada", "criterios_evaluados", "explicacion",
        "campos_implicados",
    }
    assert set(d.keys()) == esperadas
    assert d["evidencia_consultada"] == {}
    assert d["criterios_evaluados"] == []


def test_decisionengineoutput_to_dict_incluye_metadata():
    out = _build_output_minimo()
    d = out.to_dict()
    assert d["schema_version"] == SCHEMA_VERSION
    assert d["decision_global"] == RESULTADO_OBSERVAR
    assert "metadata_corrida" in d
    assert d["metadata_corrida"]["engine_run_id"] == "run-test-1"
    assert len(d["reglas_evaluadas"]) == 2
    assert len(d["hallazgos"]) == 1


def test_decisionengineoutput_to_dict_deterministic_excluye_metadata():
    out = _build_output_minimo()
    d_det = out.to_dict_deterministic()
    assert "metadata_corrida" not in d_det
    assert d_det["schema_version"] == SCHEMA_VERSION
    assert d_det["decision_global"] == RESULTADO_OBSERVAR


def test_serializacion_determinista_byte_a_byte():
    """Dos serializaciones del mismo output con sort_keys deben coincidir byte-a-byte."""
    out = _build_output_minimo()
    s1 = json.dumps(out.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    s2 = json.dumps(out.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    assert s1 == s2


def test_metadata_corrida_no_afecta_payload_deterministico():
    """Cambiar metadata_corrida NO debe alterar el payload determinista."""
    out_a = _build_output_minimo()
    out_b = _build_output_minimo()
    out_b.metadata_corrida = MetadataCorrida(
        engine_run_id="run-test-OTRO",
        engine_run_timestamp_utc="2099-12-31T23:59:59Z",
        engine_host="otro-host",
        engine_git_commit="ffffff",
    )
    s_a = json.dumps(out_a.to_dict_deterministic(), ensure_ascii=False, sort_keys=True)
    s_b = json.dumps(out_b.to_dict_deterministic(), ensure_ascii=False, sort_keys=True)
    assert s_a == s_b
