"""
Tests de integración del orquestador (Commit 3, Fase 1).

Dos fixtures sintéticos: happy path (todo OK) y degradado (todos los
estados que disparan acción humana). Ningún expediente real es tocado.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from auditoria.config import UE_ESPERADA
from auditoria.decision_engine import (
    SchemaVersionError,
    evaluar_expediente,
)
from modelo.decision_engine_output import (
    RESULTADO_NO_APLICABLE,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SCHEMA_VERSION,
)


def _escribir_expediente(tmp_path: Path, exp_dict: dict, exp_id: str = "EXP-TEST") -> Path:
    exp_dir = tmp_path / exp_id
    exp_dir.mkdir()
    (exp_dir / "expediente.json").write_text(
        json.dumps(exp_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return exp_dir


def _expediente_happy(exp_id: str = "EXP-HAPPY") -> dict:
    """Expediente sintético donde las 5 reglas deben emitir OK."""
    return {
        "schema_version": "expediente.v4",
        "expediente_id_carpeta": exp_id,
        "resolucion_id": {
            "estado_resolucion": "OK",
            "coincide_con_carpeta": True,
            "confianza_expediente": 0.99,
            "expediente_id_carpeta": exp_id,
            "expediente_id_detectado": exp_id,
        },
        "comprobantes": [
            {
                "archivo": "doc.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "ruc": "20111111111",
                "ruc_receptor": UE_ESPERADA,
                "fecha": "2026-01-01",
                "serie_numero": "F001-1",
                "monto_total": "100.00",
                "estado_consistencia": "OK",
                "tipo_tributario": "GRAVADA",
                "detalle_inconsistencia": "tipo=GRAVADA delta=0",
            },
        ],
        "validaciones": [
            {
                "tipo_validacion": "firmas_anexo3",
                "estado": "CONFORME",
                "errores": [],
                "confianza": 0.95,
                "firmantes": [],
            }
        ],
    }


def _expediente_degradado(exp_id: str = "EXP-DEGR") -> dict:
    """Expediente sintético cubriendo todos los estados que requieren acción."""
    return {
        "schema_version": "expediente.v4",
        "expediente_id_carpeta": exp_id,
        "resolucion_id": {
            "estado_resolucion": "BAJA_CONFIANZA",
            "coincide_con_carpeta": True,
            "confianza_expediente": 0.5,
            "expediente_id_carpeta": exp_id,
            "expediente_id_detectado": exp_id,
        },
        "comprobantes": [
            {
                "archivo": "doc.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "ruc": "20222222222",
                "ruc_receptor": "99999999999",  # ≠ UE_ESPERADA → OBSERVAR
                "fecha": "2026-02-01",
                "serie_numero": "F001-2",
                "monto_total": "200.00",
                "estado_consistencia": "DIFERENCIA_CRITICA",
                "tipo_tributario": "GRAVADA",
                "detalle_inconsistencia": "delta=42",
            },
            {
                "archivo": "doc.pdf",
                "pagina_inicio": 2,
                "pagina_fin": 2,
                "ruc": "20333333333",
                "ruc_receptor": None,             # ausente → REVISAR
                "fecha": "2026-02-02",
                "serie_numero": "F001-3",
                "monto_total": None,              # crítico null → REVISAR
                "estado_consistencia": "DATOS_INSUFICIENTES",
                "tipo_tributario": "",
                "detalle_inconsistencia": "monto_total=None",
            },
        ],
        "validaciones": [
            {
                "tipo_validacion": "firmas_anexo3",
                "estado": "INSUFICIENTE_EVIDENCIA",
                "errores": ["sin_firmas"],
                "confianza": 0.1,
                "firmantes": [],
            }
        ],
    }


def test_happy_path_decision_global_ok(tmp_path):
    exp_dir = _escribir_expediente(tmp_path, _expediente_happy())
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    assert out.decision_global == RESULTADO_OK
    assert len(out.reglas_evaluadas) == 5
    assert all(r.resultado == RESULTADO_OK for r in out.reglas_evaluadas)
    assert out.hallazgos == []


def test_happy_path_schema_y_input_referenciado(tmp_path):
    exp_dir = _escribir_expediente(tmp_path, _expediente_happy())
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    assert out.schema_version == SCHEMA_VERSION
    assert out.input_referenciado["expediente_schema_version"] == "expediente.v4"
    sha = out.input_referenciado["expediente_json_sha256"]
    assert isinstance(sha, str)
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)


def test_degradado_decision_global_revisar(tmp_path):
    exp_dir = _escribir_expediente(tmp_path, _expediente_degradado())
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    assert out.decision_global == RESULTADO_REVISAR
    assert len(out.reglas_evaluadas) == 5

    por_regla = {r.regla_id: r for r in out.reglas_evaluadas}
    # Ajuste 1: BAJA_CONFIANZA → REVISAR
    assert por_regla["R-IDENTIDAD-EXPEDIENTE"].resultado == RESULTADO_REVISAR
    # Mezcla CRITICA+INSUFICIENTES → REVISAR domina
    assert por_regla["R-CONSISTENCIA"].resultado == RESULTADO_REVISAR
    # monto_total None → REVISAR
    assert por_regla["R-CAMPO-CRITICO-NULL"].resultado == RESULTADO_REVISAR
    # firmas INSUFICIENTE_EVIDENCIA → REVISAR
    assert por_regla["R-FIRMAS"].resultado == RESULTADO_REVISAR
    # ruc_receptor ausente → REVISAR (dominante sobre el distinto OBSERVAR)
    assert por_regla["R-UE-RECEPTOR"].resultado == RESULTADO_REVISAR

    assert len(out.hallazgos) > 0
    # Cada hallazgo viene con resultado OBSERVAR o REVISAR (nunca OK)
    assert all(h.resultado in (RESULTADO_OBSERVAR, RESULTADO_REVISAR) for h in out.hallazgos)


def test_orden_de_reglas_es_estable(tmp_path):
    """`reglas_evaluadas` debe seguir el orden de `cargar_reglas()`."""
    exp_dir = _escribir_expediente(tmp_path, _expediente_happy())
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    ids = [r.regla_id for r in out.reglas_evaluadas]
    assert ids == [
        "R-IDENTIDAD-EXPEDIENTE",
        "R-CONSISTENCIA",
        "R-CAMPO-CRITICO-NULL",
        "R-FIRMAS",
        "R-UE-RECEPTOR",
    ]


def test_resumen_contadores_correctos(tmp_path):
    exp_dir = _escribir_expediente(tmp_path, _expediente_degradado())
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    res = out.resumen
    assert res["n_reglas_definidas"] == 5
    assert res["n_reglas_evaluadas"] == 5
    assert res["n_reglas_aplicables"] == 5
    assert set(res["por_severidad"].keys()) == {"OK", "OBSERVAR", "REVISAR", "NO_APLICABLE"}
    assert set(res["por_regla"].keys()) == {
        "R-IDENTIDAD-EXPEDIENTE",
        "R-CONSISTENCIA",
        "R-CAMPO-CRITICO-NULL",
        "R-FIRMAS",
        "R-UE-RECEPTOR",
    }
    # Cada regla degradada está en REVISAR según el fixture diseñado
    assert res["por_regla"]["R-IDENTIDAD-EXPEDIENTE"] == RESULTADO_REVISAR


def test_firmas_no_aplicable_no_eleva_decision(tmp_path):
    """Sin validacion firmas_anexo3, R-FIRMAS=NO_APLICABLE pero el resto se evalúa."""
    exp = _expediente_happy("EXP-NO-FIRMAS")
    exp["validaciones"] = []  # sin firmas
    exp_dir = _escribir_expediente(tmp_path, exp, exp_id="EXP-NO-FIRMAS")
    out = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    assert out.decision_global == RESULTADO_OK
    por_regla = {r.regla_id: r for r in out.reglas_evaluadas}
    assert por_regla["R-FIRMAS"].resultado == RESULTADO_NO_APLICABLE
    assert out.resumen["n_reglas_aplicables"] == 4


def test_schema_no_v4_lanza_error_claro(tmp_path):
    exp = _expediente_happy("EXP-V3")
    exp["schema_version"] = "expediente.v3"
    exp_dir = _escribir_expediente(tmp_path, exp, exp_id="EXP-V3")
    with pytest.raises(SchemaVersionError) as ei:
        evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    msg = str(ei.value)
    assert "expediente.v4" in msg
    assert "expediente.v3" in msg


def test_archivo_inexistente_lanza_filenotfound(tmp_path):
    no_existe = tmp_path / "no_existe"
    no_existe.mkdir()
    with pytest.raises(FileNotFoundError):
        evaluar_expediente(no_existe, incluir_metadata_corrida=False)


def test_evaluar_no_escribe_archivos(tmp_path):
    """`evaluar_expediente` solo retorna; no debe modificar el directorio."""
    exp_dir = _escribir_expediente(tmp_path, _expediente_happy())
    archivos_antes = sorted(p.name for p in exp_dir.iterdir())
    evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    archivos_despues = sorted(p.name for p in exp_dir.iterdir())
    assert archivos_antes == archivos_despues
    assert "decision_engine_output.json" not in archivos_despues
