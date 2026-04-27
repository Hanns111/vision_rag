"""
Test de idempotencia del consolidador (regla 6 del PASO 4.5).

Dos llamadas consecutivas a `consolidar()` sobre el mismo input deben
producir un dict de salida byte-idéntico tras `json.dumps(sort_keys=True)`.
Si falla, el motor 4.5 heredará no-determinismo — bloqueante para Fase 1.

Usa un fixture sintético en tmp_path duplicado intencionalmente del test
de persistencia: cada test es self-contained, no comparte estado.
"""

from __future__ import annotations

import json
from pathlib import Path

from consolidador import consolidar


def _build_fixture(tmp_path: Path, exp_id: str = "TEST-IDEMPOT-0001") -> Path:
    """Mini-expediente con 2 comprobantes para verificar determinismo."""
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
            {
                "archivo": "dummy.pdf",
                "pagina_inicio": 1,
                "pagina_fin": 1,
                "tipo": "factura_electronica",
                "ruc": "20611798637",
                "ruc_receptor": "20380795907",
                "razon_social": "TEST EMISOR A",
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
                "hash_deduplicacion": "HASH_A",
                "texto_resumen": "test A",
            },
            {
                "archivo": "dummy.pdf",
                "pagina_inicio": 2,
                "pagina_fin": 2,
                "tipo": "factura_electronica",
                "ruc": "20612666751",
                "ruc_receptor": "20380795907",
                "razon_social": "TEST EMISOR B",
                "serie_numero": "F001-101",
                "fecha": "2026-02-09",
                "monto_total": "100.00",
                "moneda": "PEN",
                "monto_igv": "15.25",
                "bi_gravado": "84.75",
                "op_exonerada": None,
                "op_inafecta": None,
                "recargo_consumo": None,
                "confianza": 1.0,
                "hash_deduplicacion": "HASH_B",
                "texto_resumen": "test B",
            },
        ],
    }
    (extractions_dir / "dummy.pdf.json").write_text(
        json.dumps(extraction, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return exp_dir


def test_idempotencia_consolidador_byte_a_byte(tmp_path):
    """Dos consolidar() sobre el mismo input → JSON byte-idéntico."""
    exp_dir = _build_fixture(tmp_path)

    e1 = consolidar(exp_dir)
    e2 = consolidar(exp_dir)

    s1 = json.dumps(e1.to_dict(), ensure_ascii=False, sort_keys=True, indent=2)
    s2 = json.dumps(e2.to_dict(), ensure_ascii=False, sort_keys=True, indent=2)

    assert s1 == s2, "Output no determinista entre 2 corridas del consolidador"
