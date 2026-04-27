"""
Test de persistencia del consolidador (PRE-PASO 4.5 / D-24).

Confirma que `consolidar()` poblará en cada `Comprobante` los 4 campos
nuevos del schema `expediente.v4`:
  - ruc_receptor (propagado desde extractions/*.json)
  - estado_consistencia (calculado en el consolidador)
  - tipo_tributario (calculado en el consolidador)
  - detalle_inconsistencia (calculado en el consolidador)

Usa un fixture sintético en tmp_path: NO toca expedientes reales en
control_previo/procesados/.
"""

from __future__ import annotations

import json
from pathlib import Path

from consolidador import consolidar, escribir_expediente_json


def _build_fixture(tmp_path: Path, exp_id: str = "TEST-PERS-0001") -> Path:
    """Construye un mini-expediente con 2 comprobantes sintéticos:
    uno OK GRAVADA y uno DIFERENCIA_CRITICA. Sin OCR, sin pipeline real.
    """
    exp_dir = tmp_path / exp_id
    exp_dir.mkdir()

    metadata = {
        "expediente_id": exp_id,
        "documentos": [
            {"nombre": "dummy.pdf", "sha1": "abc123", "paginas": 1}
        ],
    }
    (exp_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    extractions_dir = exp_dir / "extractions"
    extractions_dir.mkdir()

    extraction = {
        "archivo": "dummy.pdf",
        "expediente_id": exp_id,
        "comprobantes": [
            # Comprobante OK GRAVADA: bi+igv = 35.00 = total → delta 0 → OK
            {
                "archivo": "dummy.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "tipo": "factura_electronica",
                "ruc": "20611798637",
                "ruc_receptor": "20380795907",
                "razon_social": "TEST EMISOR OK",
                "serie_numero": "F001-100",
                "fecha": "2026-02-08",
                "monto_total": "35.00",
                "moneda": "PEN",
                "monto_igv": "5.34",
                "bi_gravado": "29.66",
                "op_exonerada": None,
                "op_inafecta": None,
                "recargo_consumo": None,
                "confianza": 1.0,
                "hash_deduplicacion": "HASH_OK",
                "texto_resumen": "comprobante ok gravada test",
            },
            # Comprobante DIFERENCIA_CRITICA: bi+igv = 35.00, total = 85.00 → delta 50.00
            {
                "archivo": "dummy.pdf",
                "pagina_inicio": 2,
                "pagina_fin": 2,
                "tipo": "factura_electronica",
                "ruc": "20612666751",
                "ruc_receptor": "20380795907",
                "razon_social": "TEST EMISOR CRITICA",
                "serie_numero": "F001-101",
                "fecha": "2026-02-09",
                "monto_total": "85.00",
                "moneda": "PEN",
                "monto_igv": "5.34",
                "bi_gravado": "29.66",
                "op_exonerada": None,
                "op_inafecta": None,
                "recargo_consumo": None,
                "confianza": 1.0,
                "hash_deduplicacion": "HASH_CRITICA",
                "texto_resumen": "comprobante con diferencia critica test",
            },
        ],
    }
    (extractions_dir / "dummy.pdf.json").write_text(
        json.dumps(extraction, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return exp_dir


def test_persistencia_4_campos_en_dataclass(tmp_path):
    """consolidar() debe poblar los 4 campos PRE-PASO 4.5 en cada Comprobante."""
    exp_dir = _build_fixture(tmp_path)
    expediente = consolidar(exp_dir)

    assert expediente.schema_version == "expediente.v4"
    assert len(expediente.comprobantes) == 2

    c_ok = next(c for c in expediente.comprobantes if c.hash_deduplicacion == "HASH_OK")
    assert c_ok.ruc_receptor == "20380795907"
    assert c_ok.estado_consistencia == "OK"
    assert c_ok.tipo_tributario == "GRAVADA"
    assert "tipo=GRAVADA" in c_ok.detalle_inconsistencia

    c_critica = next(
        c for c in expediente.comprobantes if c.hash_deduplicacion == "HASH_CRITICA"
    )
    assert c_critica.ruc_receptor == "20380795907"
    assert c_critica.estado_consistencia == "DIFERENCIA_CRITICA"
    assert c_critica.tipo_tributario == "GRAVADA"


def test_persistencia_4_campos_en_json(tmp_path):
    """to_dict() debe serializar los 4 campos al expediente.json escrito a disco."""
    exp_dir = _build_fixture(tmp_path, exp_id="TEST-PERS-JSON-0002")
    expediente = consolidar(exp_dir)
    out_path = escribir_expediente_json(expediente, exp_dir)

    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "expediente.v4"

    for c in data["comprobantes"]:
        assert "ruc_receptor" in c
        assert "estado_consistencia" in c
        assert "tipo_tributario" in c
        assert "detalle_inconsistencia" in c

    c_ok = next(c for c in data["comprobantes"] if c["hash_deduplicacion"] == "HASH_OK")
    assert c_ok["ruc_receptor"] == "20380795907"
    assert c_ok["estado_consistencia"] == "OK"
    assert c_ok["tipo_tributario"] == "GRAVADA"
