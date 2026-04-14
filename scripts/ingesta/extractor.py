"""
Wrapper del extractor PASO 4.1 para el pipeline de ingesta.

- Entrada: texto extraído + tipo detectado por classifier.
- Salida: dict con valores + confianza por campo, listo para el Excel.
- No reimplementa reglas: delega a `piloto_field_extract_paso4.extract_fields_paso4`.

Campo derivado: `tipo_gasto` se infiere del tipo_documento_detectado (mapeo
conservador; si no hay señal clara → "desconocido"). No inventa RUCs/montos.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_scripts = str(Path(__file__).resolve().parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)


@dataclass
class CampoExtraido:
    valor: str | None
    confianza: float
    regla: str


@dataclass
class ExtractionResult:
    monto: CampoExtraido
    fecha: CampoExtraido
    ruc: CampoExtraido
    razon_social: CampoExtraido
    numero_documento: CampoExtraido
    tipo_gasto: CampoExtraido
    texto_resumen: str
    tipo_doc_interno: str
    trace_raw: dict[str, Any] = field(default_factory=dict)


# Mapeo tipo documental (clasificador o extractor interno) → tipo_gasto genérico
_TIPO_GASTO_MAP: dict[str, str] = {
    "rendicion": "viaticos",
    "solicitud": "viaticos",
    "planilla_viaticos": "viaticos",
    "solicitud_viaticos": "viaticos",
    "pasaje": "pasaje_aereo",
    "orden_servicio": "servicios",
    "orden_compra": "bienes",
    "factura": "sustento",
    "informe_comision": "viaticos",
    "nota_pago": "desconocido",
    "ri": "devolucion_viaticos",
    "anexo": "desconocido",
    "oficio": "desconocido",
    "otros": "desconocido",
    "tipo_desconocido": "desconocido",
}


def _regla_a_confianza(regla: str | None) -> float:
    """Convierte el id de regla del extractor a confianza heurística ∈ [0, 1]."""
    if not regla:
        return 0.0
    r = regla.lower()
    if r.endswith("_none") or "fallback_desconocido" in r or r == "none":
        return 0.0
    if "fallback" in r or "skip" in r or "no_extraido" in r or "no_campo" in r or "sin_campo" in r:
        return 0.4
    if "global_plain" in r or "primera_etiqueta" in r:
        return 0.6
    return 0.85


def _campo_desde_trace(valor: Any, trace_entry: dict[str, Any]) -> CampoExtraido:
    regla = str(trace_entry.get("regla") or "")
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return CampoExtraido(valor=None, confianza=0.0, regla=regla or "sin_regla")
    return CampoExtraido(valor=str(valor), confianza=_regla_a_confianza(regla), regla=regla)


def _primer_monto_no_nulo(
    fields: dict[str, Any], trace: dict[str, Any]
) -> CampoExtraido:
    for clave in ("monto_total", "monto_subtotal"):
        v = fields.get(clave)
        t = trace.get(clave, {}) if isinstance(trace.get(clave), dict) else {}
        if v:
            return _campo_desde_trace(v, t)
    return CampoExtraido(valor=None, confianza=0.0, regla="monto_none")


def _inferir_tipo_gasto(tipo_clasificador: str, tipo_interno: str) -> CampoExtraido:
    candidato = _TIPO_GASTO_MAP.get(tipo_clasificador) or _TIPO_GASTO_MAP.get(tipo_interno)
    if not candidato or candidato == "desconocido":
        return CampoExtraido(
            valor="desconocido",
            confianza=0.0,
            regla=f"mapa_tipo_doc:{tipo_clasificador}/{tipo_interno}",
        )
    return CampoExtraido(
        valor=candidato,
        confianza=0.7,
        regla=f"mapa_tipo_doc:{tipo_clasificador}/{tipo_interno}",
    )


def _texto_resumen(texto: str, max_chars: int = 400) -> str:
    """Primeros max_chars chars útiles (salta marcador de página y normaliza saltos)."""
    if not texto:
        return ""
    import re

    m = re.search(r"=====\s*PAGE\s+1\b.*?=====\s*", texto)
    start = m.end() if m else 0
    sample = texto[start : start + max_chars * 3]
    sample = re.sub(r"\s+", " ", sample).strip()
    return sample[:max_chars]


def extract_campos(texto: str, tipo_clasificador: str) -> ExtractionResult:
    """
    Extrae campos del esquema Excel desde texto OCR + categoría detectada.

    Usa `piloto_field_extract_paso4.extract_fields_paso4` tal cual.
    """
    from piloto_field_extract_paso4 import extract_fields_paso4

    fields, trace = extract_fields_paso4(texto or "")
    tipo_interno = str(fields.get("tipo_documento") or "desconocido")

    ruc = _campo_desde_trace(fields.get("ruc_emisor"), trace.get("ruc_emisor", {}))
    razon = _campo_desde_trace(
        fields.get("razon_social_emisor"), trace.get("razon_social_emisor", {})
    )
    numero = _campo_desde_trace(fields.get("serie_numero"), trace.get("serie_numero", {}))
    fecha = _campo_desde_trace(fields.get("fecha_emision"), trace.get("fecha_emision", {}))
    monto = _primer_monto_no_nulo(fields, trace)
    tipo_gasto = _inferir_tipo_gasto(tipo_clasificador, tipo_interno)

    return ExtractionResult(
        monto=monto,
        fecha=fecha,
        ruc=ruc,
        razon_social=razon,
        numero_documento=numero,
        tipo_gasto=tipo_gasto,
        texto_resumen=_texto_resumen(texto),
        tipo_doc_interno=tipo_interno,
        trace_raw={"fields": fields, "trace": trace},
    )
