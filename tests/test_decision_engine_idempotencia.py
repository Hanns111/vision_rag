"""
Test de idempotencia del orquestador (regla 6 de PASO 4.5).

Sobre el mismo input, dos llamadas a `evaluar_expediente()` deben producir
un payload determinista byte-idéntico tras `json.dumps(sort_keys=True)`.
La idempotencia se verifica sobre `to_dict_deterministic()` — el sub-objeto
`metadata_corrida` (timestamps + uuid + host + git_commit) está aislado por
diseño y no participa del diff.
"""

from __future__ import annotations

import json
from pathlib import Path

from auditoria.decision_engine import evaluar_expediente


def _expediente_v4(exp_id: str = "EXP-IDEMPOT") -> dict:
    """Mezcla deliberada de OK / DIFERENCIA_LEVE / nulls / firmas observadas."""
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
                "archivo": "a.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "ruc": "20111111111",
                "ruc_receptor": "20380795907",
                "fecha": "2026-01-01",
                "serie_numero": "F001-1",
                "monto_total": "100.00",
                "estado_consistencia": "OK",
                "tipo_tributario": "GRAVADA",
                "detalle_inconsistencia": "tipo=GRAVADA delta=0",
            },
            {
                "archivo": "a.pdf",
                "pagina_inicio": 2,
                "pagina_fin": 2,
                "ruc": "20222222222",
                "ruc_receptor": None,
                "fecha": None,
                "serie_numero": "F001-2",
                "monto_total": "50.00",
                "estado_consistencia": "DIFERENCIA_LEVE",
                "tipo_tributario": "GRAVADA",
                "detalle_inconsistencia": "delta=2",
            },
        ],
        "validaciones": [
            {
                "tipo_validacion": "firmas_anexo3",
                "estado": "OBSERVADO",
                "errores": ["rol_no_detectado:jefe_unidad"],
                "confianza": 0.6,
                "firmantes": [],
            }
        ],
    }


def _escribir(tmp_path: Path, exp_dict: dict, exp_id: str = "EXP-IDEMPOT") -> Path:
    exp_dir = tmp_path / exp_id
    exp_dir.mkdir()
    (exp_dir / "expediente.json").write_text(
        json.dumps(exp_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return exp_dir


def test_idempotencia_payload_determinista_byte_a_byte(tmp_path):
    """Dos `evaluar_expediente()` consecutivas → JSON byte-idéntico."""
    exp_dir = _escribir(tmp_path, _expediente_v4())
    a = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    b = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    sa = json.dumps(a.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    sb = json.dumps(b.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    assert sa == sb


def test_metadata_corrida_no_rompe_payload_determinista(tmp_path):
    """Aún cuando `metadata_corrida` difiere (timestamps + uuid distintos
    entre corridas), el sub-objeto determinista debe ser igual."""
    exp_dir = _escribir(tmp_path, _expediente_v4())
    a = evaluar_expediente(exp_dir, incluir_metadata_corrida=True)
    b = evaluar_expediente(exp_dir, incluir_metadata_corrida=True)
    assert a.metadata_corrida is not None
    assert b.metadata_corrida is not None
    sa = json.dumps(a.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    sb = json.dumps(b.to_dict_deterministic(), ensure_ascii=False, sort_keys=True, indent=2)
    assert sa == sb


def test_orden_de_hallazgos_estable(tmp_path):
    """Los hallazgos deben venir ordenados igual en ambas corridas."""
    exp_dir = _escribir(tmp_path, _expediente_v4())
    a = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    b = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    pares_a = [(h.regla_id, h.scope, h.objeto_id) for h in a.hallazgos]
    pares_b = [(h.regla_id, h.scope, h.objeto_id) for h in b.hallazgos]
    assert pares_a == pares_b
    # Y debe estar realmente ordenado por (regla_id, scope, objeto_id)
    assert pares_a == sorted(pares_a)


def test_sha256_input_es_estable_si_archivo_no_cambia(tmp_path):
    exp_dir = _escribir(tmp_path, _expediente_v4())
    a = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    b = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)
    assert (
        a.input_referenciado["expediente_json_sha256"]
        == b.input_referenciado["expediente_json_sha256"]
    )


def test_sha256_cambia_si_input_cambia(tmp_path):
    """Si el `expediente.json` cambia un byte, el sha256 cambia."""
    exp_dir = _escribir(tmp_path, _expediente_v4())
    a = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)

    json_path = exp_dir / "expediente.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    data["expediente_id_carpeta"] = "EXP-DIFERENTE"
    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    b = evaluar_expediente(exp_dir, incluir_metadata_corrida=False)

    assert (
        a.input_referenciado["expediente_json_sha256"]
        != b.input_referenciado["expediente_json_sha256"]
    )
