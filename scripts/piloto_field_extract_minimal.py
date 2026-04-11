"""
Extracción mínima de campos desde texto plano — solo para evaluación PASO 2 (bake-off).

No es parsing de producto (eso es PASO 4). Mismas heurísticas para todos los motores
para mantener comparabilidad relativa. Campos débiles (tipo_documento, razón social)
pueden quedar en null si no hay patrón claro.
"""

from __future__ import annotations

import re
from typing import Any

_FIELD_KEYS = [
    "ruc_emisor",
    "tipo_documento",
    "serie_numero",
    "fecha_emision",
    "moneda",
    "monto_subtotal",
    "monto_igv",
    "monto_total",
    "ruc_receptor",
    "razon_social_emisor",
]


def _norm_amount(s: str | None) -> float | None:
    if not s:
        return None
    t = s.strip().replace(",", "").replace("S/", "").replace("S/ ", "")
    t = re.sub(r"[^\d.]", "", t)
    if not t:
        return None
    try:
        return round(float(t), 2)
    except ValueError:
        return None


def _norm_date(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return s
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    return None


def extract_fields_minimal(text: str) -> dict[str, Any]:
    """Devuelve dict con claves del esquema; valores string o null."""
    if not text:
        return {k: None for k in _FIELD_KEYS}

    t = text
    upper = t.upper()

    rucs = re.findall(r"\b\d{11}\b", t)
    ruc_emisor = rucs[0] if rucs else None
    ruc_receptor = None
    for r in rucs[1:]:
        if r != ruc_emisor:
            ruc_receptor = r
            break

    serie_numero = None
    m = re.search(r"\b([EF]\d{3}-\d{1,7})\b", t, re.I)
    if m:
        serie_numero = m.group(1).upper()
    if not serie_numero:
        m = re.search(r"\bN[°º]?\s*(\d{5})\b", t, re.I)
        if m:
            serie_numero = m.group(1)

    fecha_emision = None
    for m in re.finditer(r"\b(\d{4}-\d{2}-\d{2})\b", t):
        fecha_emision = m.group(1)
        break
    if not fecha_emision:
        for m in re.finditer(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", t):
            fecha_emision = _norm_date(m.group(1))
            break

    moneda = None
    if re.search(r"\bPEN\b", upper) or "S/" in t:
        moneda = "PEN"
    if re.search(r"\bUSD\b", upper):
        moneda = "USD"

    def grab_amount_after(label: str) -> str | None:
        pat = rf"{label}[^\d]*([\d]+[.,]\d{{2}})"
        m = re.search(pat, t, re.I)
        if m:
            return m.group(1).replace(",", ".")
        return None

    monto_subtotal = grab_amount_after("Sub Total") or grab_amount_after("SUB TOTAL")
    monto_igv = grab_amount_after("IGV")
    monto_total = grab_amount_after("Total") or grab_amount_after("IMPORTE")

    tipo_documento = None
    if "FACTURA" in upper and "ELECTR" in upper:
        tipo_documento = "01"
    elif "INFORME" in upper and "COMISI" in upper:
        tipo_documento = "informe_comision"
    elif "SOLICITUD" in upper and ("VIATIC" in upper or "VIÁTIC" in upper):
        tipo_documento = "solicitud_viaticos"

    razon_social_emisor = None
    m = re.search(r"(?:R\.?U\.?C\.?\s*:?\s*\d{11}\s*\n?\s*)([^\n]{4,80})", t)
    if m:
        razon_social_emisor = m.group(1).strip()[:120]

    return {
        "ruc_emisor": ruc_emisor,
        "tipo_documento": tipo_documento,
        "serie_numero": serie_numero,
        "fecha_emision": fecha_emision,
        "moneda": moneda,
        "monto_subtotal": monto_subtotal,
        "monto_igv": monto_igv,
        "monto_total": monto_total,
        "ruc_receptor": ruc_receptor,
        "razon_social_emisor": razon_social_emisor,
    }


def gold_pred_match(campo: str, gold: Any, pred: Any) -> bool:
    """Exactitud 0/1 según roadmap §4.3 (tolerancia montos ±0.01)."""
    if gold is None:
        return True  # no cuenta en agregados; caller filtra
    if pred is None:
        return False
    if campo in ("monto_subtotal", "monto_igv", "monto_total"):
        g = _norm_amount(str(gold))
        p = _norm_amount(str(pred))
        if g is None or p is None:
            return False
        return abs(g - p) <= 0.01
    if campo == "fecha_emision":
        return _norm_date(str(gold)) == _norm_date(str(pred))
    if campo in ("ruc_emisor", "ruc_receptor", "serie_numero", "tipo_documento", "moneda"):
        return str(gold).strip().upper() == str(pred).strip().upper()
    if campo == "razon_social_emisor":
        return str(gold).strip().upper() == str(pred).strip().upper()
    return False
