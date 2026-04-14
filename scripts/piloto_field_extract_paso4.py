"""
PASO 4 — Extracción por reglas deterministas + traza JSON por campo.

Entrada: texto OCR ya producido (sin OCR aquí). Salida alineada al esquema piloto.
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

_EXCLUDE_RAZON = re.compile(
    r"FACTURA|ELECTR|R\.?U\.?C\.?|HTTP|WWW\.|@|^\s*D\.?\s*Comercial|"
    r"De:\s*$|^\s*Cliente\s*$|^\s*Direcci",
    re.I,
)


def _empty_trace_field(tipo: str) -> dict[str, Any]:
    return {"tipo_doc_inferido": tipo, "regla": None, "lineas_usadas": []}


def _trace(tipo: str, regla: str, lineas: list[str]) -> dict[str, Any]:
    return {
        "tipo_doc_inferido": tipo,
        "regla": regla,
        "lineas_usadas": lineas[:12],
    }


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


def _norm_amount_str(s: str | None) -> str | None:
    if not s:
        return None
    t = s.strip().replace(",", ".")
    t = re.sub(r"[^\d.]", "", t)
    if not t:
        return None
    try:
        return f"{round(float(t), 2):.2f}"
    except ValueError:
        return None


def _find_rucs_with_context(text: str) -> list[tuple[str, str]]:
    """Lista (ruc, línea completa donde aparece)."""
    out: list[tuple[str, str]] = []
    for line in text.splitlines():
        for m in re.finditer(r"\b(\d{11})\b", line):
            out.append((m.group(1), line.strip()))
    return out


_MESES_ES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def _fecha_informe_comision(text: str) -> tuple[str | None, str, list[str]]:
    """Fecha desde encabezado tipo '27 de febrero de 2026' (primer match en cabeza)."""
    head = "\n".join(text.splitlines()[:30])
    m = re.search(r"\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b", head, re.I)
    if m:
        d, mn_w, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        mo = _MESES_ES.get(mn_w)
        if mo:
            return f"{y:04d}-{mo:02d}-{d:02d}", "informe_fecha_texto_es", [m.group(0)]
    return None, "informe_fecha_none", []


def _fecha_moneda(text: str, upper: str) -> tuple[str | None, str | None]:
    fecha = None
    for m in re.finditer(r"\b(\d{4}-\d{2}-\d{2})\b", text):
        fecha = m.group(1)
        break
    if not fecha:
        for m in re.finditer(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", text):
            fecha = _norm_date(m.group(1))
            break
    moneda = None
    if re.search(r"\bPEN\b", upper) or "S/" in text:
        moneda = "PEN"
    if re.search(r"\bUSD\b", upper):
        moneda = "USD"
    return fecha, moneda


def _detect_tipo_documental(text: str) -> tuple[str, str]:
    """
    Devuelve (tipo_doc, regla_deteccion).
    tipos: factura, ri, nota_pago, planilla_viaticos, solicitud_viaticos,
    informe_comision, anexo_informe, desconocido
    """
    u = text.upper()
    # Orden: más específico primero
    if re.search(r"INFORME\s+DE\s+COMISI", u):
        return "informe_comision", "anchor_informe_comision"
    if re.search(r"NOTA\s+DE\s+PAGO", u):
        return "nota_pago", "anchor_nota_pago"
    if "PLANILLA" in u and ("VIÁTIC" in text.upper() or "VIATIC" in u):
        return "planilla_viaticos", "anchor_planilla_viaticos"
    if "SOLICITUD" in u and ("VIÁTIC" in text.upper() or "VIATIC" in u):
        return "solicitud_viaticos", "anchor_solicitud_viaticos"
    if "FACTURA" in u and "ELECTR" in u:
        return "factura", "anchor_factura_electronica"
    if re.search(r"DEVOLUCI", text, re.I):
        if re.search(r"VI[ÁA]TIC", text, re.I):
            return "ri", "anchor_devolucion_viaticos"
    if "RECIBO" in u and "INGRES" in u:
        return "ri", "anchor_recibo_ingreso"
    if "REPRESENTACIÓN IMPRESA" in u or "REPRESENTACION IMPRESA" in u:
        if "FACTURA" in u:
            return "factura", "anchor_repr_impresa_factura"
    if re.search(r"Tarea\s+Programada", text, re.I) and re.search(r"\bD[IÍ]A\s*:", text, re.I):
        if "FACTURA" not in u and "NOTA DE PAGO" not in u and "PLANILLA DE VI" not in u:
            return "anexo_informe", "anchor_anexo_cuerpo_narrativo"
    if "ANEXO" in u and ("INFORME" in u or "COMISI" in u):
        return "anexo_informe", "anchor_anexo_titulo"
    return "desconocido", "fallback_desconocido"


def _factura_split_head_body(text: str) -> tuple[str, str]:
    m = re.search(r"\bCliente\s*:", text, re.I)
    if m:
        return text[: m.start()], text[m.start() :]
    return text, ""


def _factura_rucs(head: str, body: str) -> tuple[str | None, str | None, list[str]]:
    lineas_trace: list[str] = []
    ruc_em = None
    ruc_rec = None
    for line in head.splitlines():
        mm = re.search(r"R\.?U\.?C\.?\s*:?\s*(\d{11})|\bRUC\s+(\d{11})", line, re.I)
        if mm:
            r = mm.group(1) or mm.group(2)
            if not ruc_em:
                ruc_em = r
                lineas_trace.append(line.strip())
    if body:
        mm = re.search(
            r"Cliente\s*:.*?(?:R\.?U\.?C\.?\s*:?\s*|RUC\s*:?\s*)(\d{11})",
            body,
            re.I | re.DOTALL,
        )
        if mm:
            ruc_rec = mm.group(1)
            lineas_trace.append(mm.group(0).replace("\n", " ")[:120])
        else:
            body_join = re.sub(r"\n\s*:\s*", " : ", body)
            for line in body_join.splitlines():
                mm = re.search(r"R\.?U\.?C\.?\s*:?\s*(\d{11})|\bRUC\s*:?\s*(\d{11})", line, re.I)
                if mm:
                    r = mm.group(1) or mm.group(2)
                    if r != ruc_em:
                        ruc_rec = r
                        lineas_trace.append(line.strip())
                        break
    if ruc_em and not ruc_rec:
        all_r = re.findall(r"\b(\d{11})\b", head + "\n" + body)
        seen: list[str] = []
        for r in all_r:
            if r not in seen:
                seen.append(r)
        if len(seen) >= 2:
            ruc_rec = seen[1]
            lineas_trace.append(f"fallback_segundo_ruc_en_documento:{ruc_rec}")
    return ruc_em, ruc_rec, lineas_trace


def _factura_serie(text: str, head: str) -> tuple[str | None, str, list[str]]:
    pat = r"\bN?[º°]?\s*([EF]\d{3}-\d{2,8})\b"
    for line in head.splitlines():
        m = re.search(pat, line, re.I)
        if m:
            return m.group(1).upper(), "factura_serie_FE_patron", [line.strip()]
    m = re.search(r"\bN[º°]\s*([EF]\d{3}-\d{2,8})\b", text, re.I)
    if m:
        return m.group(1).upper(), "factura_serie_FE_global", [m.group(0)]
    m = re.search(r"\b([EF]\d{3}-\d{2,8})\b", text, re.I)
    if m:
        return m.group(1).upper(), "factura_serie_FE_global_plain", [m.group(0)]
    return None, "factura_serie_none", []


def _factura_montos(text: str) -> tuple[dict[str, str | None], str, list[str]]:
    """Devuelve dict subkeys + regla + líneas usadas (fragmentos)."""
    tflat = re.sub(r"\s+", " ", text)
    lineas: list[str] = []
    sub = igv = tot = None
    reglas: list[str] = []

    def grab(pat: str, name: str) -> str | None:
        nonlocal lineas
        m = re.search(pat, tflat, re.I)
        if m:
            v = _norm_amount_str(m.group(1))
            if v:
                reglas.append(name)
                lineas.append(m.group(0)[:120])
                return v
        return None

    sub = grab(r"(?:Op\.?\s*Gravadas?|Venta\s+Gravada)\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_op_gravada")
    if not sub:
        sub = grab(r"SUB\s*TOTAL\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_subtotal_label")

    igv = grab(r"IGV\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_igv")
    if not igv:
        igv = grab(r"Total\s+I\.?G\.?V\.?\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_igv_total")

    tot = grab(r"Total\s+a\s+pagar\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_total_pagar")
    if not tot:
        tot = grab(r"Total\s+Precio\s+de\s+Venta\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_total_precio_venta")
    if not tot:
        tot = grab(r"IMPORTE\s+TOTAL\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_importe_total")
    if not tot:
        tot = grab(r"\bTotal\s*:?\s*S/?\s*([\d]+[.,]\d{2})", "monto_total_generico")

    regla = "+".join(reglas) if reglas else "monto_none"
    return (
        {"monto_subtotal": sub, "monto_igv": igv, "monto_total": tot},
        regla,
        lineas,
    )


def _factura_razon_social(head: str) -> tuple[str | None, str, list[str]]:
    lines = [ln.strip() for ln in head.splitlines() if ln.strip()]
    ruc_idx = None
    for i, ln in enumerate(lines):
        if re.search(r"R\.?U\.?C\.?\s*:?\s*\d{11}|\bRUC\s+\d{11}", ln, re.I):
            ruc_idx = i
            break
    candidates = lines[:ruc_idx] if ruc_idx is not None else lines[:15]
    parts: list[str] = []
    for ln in candidates:
        if _EXCLUDE_RAZON.search(ln) or len(ln) < 3:
            continue
        if re.match(r"^[\d\s.,$/\-]+$", ln):
            continue
        parts.append(ln)
        if sum(len(p) for p in parts) > 28:
            break
    if not parts:
        return None, "razon_none", []
    name = " ".join(parts).strip()[:120]
    return name, "razon_lineas_previas_a_ruc", parts[:5]


def _normalize_nota_serie(raw: str) -> str:
    raw = raw.strip()
    m = re.match(r"^(\d{4})[.](\d{2})[.](\d{2})[.](\d+)$", raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}-{m.group(4)}"
    return raw.replace(".", "-")


def _nota_serie(text: str) -> tuple[str | None, str, list[str]]:
    for line in text.splitlines()[:5]:
        m = re.search(
            r"NOTA\s+DE\s+PAGO[^\d]{0,20}([\d]{4}[.\-][\d]{2}[.\-][\d]{2}[.\-][\d]+|[\d.\-]{12,})",
            line,
            re.I,
        )
        if m:
            s = _normalize_nota_serie(m.group(1))
            return s, "nota_serie_linea_encabezado", [line.strip()]
    return None, "nota_serie_none", []


def _nota_ruc_emisor(text: str) -> tuple[str | None, str, list[str]]:
    """RUC en bloque institucional (PROGRAMA / MINEDU / UNIDAD EJECUTORA)."""
    lines = text.splitlines()
    for i, line in enumerate(lines[:40]):
        lu = line.upper()
        if "PROGRAMA EDUCACION" in lu or "MINEDU" in lu or "UNIDAD EJECUTORA" in lu:
            window = "\n".join(lines[i : min(i + 5, len(lines))])
            m = re.search(r"(?:R\.?U\.?C\.?\s*:?\s*|RUC\s*:?\s*)(\d{11})", window, re.I)
            if m:
                return m.group(1), "nota_ruc_ventana_institucional", [ln.strip() for ln in lines[i : i + 5]]
    for line in lines[:25]:
        m = re.search(r"(?:R\.?U\.?C\.?\s*:?\s*|RUC\s*:?\s*)(\d{11})", line, re.I)
        if m:
            return m.group(1), "nota_ruc_primera_etiqueta", [line.strip()]
    return None, "nota_ruc_none", []


def _planilla_solicitud_serie(text: str, tipo: str) -> tuple[str | None, str, list[str]]:
    if tipo == "planilla_viaticos":
        m = re.search(
            r"(\d{5,6})\s*\n\s*PLANILLA\s+DE\s+VI[ÁA]TICOS",
            text,
            re.I,
        )
        if m:
            return m.group(1), "planilla_numero_antes_titulo", [m.group(0).replace("\n", " | ")]
        m = re.search(
            r"PLANILLA\s+DE\s+VI[ÁA]TICOS\s*N[º°]?\s*:?\s*\n\s*(\d{5,6})",
            text,
            re.I,
        )
        if m:
            return m.group(1), "planilla_numero_despues_titulo", [m.group(0).replace("\n", " | ")]
    if tipo == "solicitud_viaticos":
        m = re.search(
            r"SOLICITUD\s+DE\s+VI[ÁA]TICOS[^\n]*(?:\n[^\S\r\n]*)+\n?\s*(\d{5,6})",
            text,
            re.I,
        )
        if m:
            return m.group(1), "solicitud_numero_bajo_titulo", [m.group(0).replace("\n", " | ")]
    return None, "planilla_solicitud_serie_none", []


def _planilla_solicitud_ruc(text: str) -> tuple[str | None, str, list[str]]:
    lines = text.splitlines()
    for i, line in enumerate(lines[:35]):
        lu = line.upper()
        if "PROGRAMA EDUCACION" in lu or "MINISTERIO" in lu or "MINEDU" in lu or "UNIDAD EJECUTORA" in lu:
            window = "\n".join(lines[max(0, i - 2) : min(i + 8, len(lines))])
            for m in re.finditer(r"\b(\d{11})\b", window):
                if m.group(1).startswith("10") or m.group(1).startswith("20"):
                    chunk = [ln.strip() for ln in lines[max(0, i - 2) : min(i + 8, len(lines))]]
                    return m.group(1), "ruc_ventana_programa_minedu", chunk
    return None, "planilla_ruc_none", []


def _planilla_monto_total(text: str) -> tuple[str | None, str, list[str]]:
    m = re.search(r"Total\s*:?\s*\n\s*([\d]+[.,]\d{2})\b", text, re.I | re.M)
    if m:
        return _norm_amount_str(m.group(1)), "planilla_total_linea_siguiente", [m.group(0).strip()]
    m = re.search(r"Total\s*:?\s*([\d]+[.,]\d{2})\b", text, re.I)
    if m:
        return _norm_amount_str(m.group(1)), "planilla_total_misma_linea", [m.group(0).strip()]
    return None, "planilla_total_none", []


def _ri_serie(text: str) -> tuple[str | None, str, list[str]]:
    m = re.search(r"\b900\s*-\s*4\s*-\s*2026\b", text)
    if m:
        return "900-4-2026", "ri_serie_literal", [m.group(0)]
    flat = re.sub(r"\s+", " ", text)
    m = re.search(r"900\D{0,3}9\D{0,3}4\D{0,3}2026", flat)
    if m:
        return "900-4-2026", "ri_serie_flexible_ocr_multilinea", [m.group(0).strip()[:40]]
    m = re.search(r"900\D{0,8}4\D{0,8}2026", flat)
    if m:
        return "900-4-2026", "ri_serie_flexible_900_4_2026", [m.group(0).strip()[:40]]
    return None, "ri_serie_none", []


def _ri_monto_total(text: str) -> tuple[str | None, str, list[str]]:
    m = re.search(r"TOTAL\s+S/?\.?\s*([\d]+[.,]\d{2})", text, re.I)
    if m:
        v = _norm_amount_str(m.group(1))
        if v:
            return v, "ri_total_cerca_label", [m.group(0).strip()]
    m = re.search(r"([\d]+[.,]\d{2})\s*\n\s*DATOS\s+GENERALES", text, re.I)
    if m:
        v = _norm_amount_str(m.group(1))
        if v:
            return v, "ri_total_antes_datos_generales", [m.group(0).strip()]
    return None, "ri_total_none", []


def _ri_ruc(text: str) -> tuple[str | None, str, list[str]]:
    m = re.search(r"RUC\s*N[°º]?\s*:?\s*(\d{11})", text, re.I)
    if m:
        return m.group(1), "ri_ruc_etiqueta", [m.group(0).strip()]
    return None, "ri_ruc_none", []


def extract_fields_paso4(text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Extrae campos y traza determinista.

    Returns:
        (fields_dict, trace_dict) — trace_dict[campo] = {tipo_doc_inferido, regla, lineas_usadas}
    """
    fields: dict[str, Any] = {k: None for k in _FIELD_KEYS}
    trace: dict[str, Any] = {k: _empty_trace_field("desconocido") for k in _FIELD_KEYS}

    if not (text or "").strip():
        return fields, trace

    tipo_doc, regla_tipo = _detect_tipo_documental(text)
    upper = text.upper()

    fecha, moneda = _fecha_moneda(text, upper)
    fields["fecha_emision"] = fecha
    fields["moneda"] = moneda
    trace["fecha_emision"] = _trace(tipo_doc, "shared_fecha_primer_iso_o_slash", [])
    trace["moneda"] = _trace(tipo_doc, "shared_moneda_pen_usd", [])

    # --- Por tipo ---
    if tipo_doc == "anexo_informe":
        fields["tipo_documento"] = "anexo_informe"
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        for k in _FIELD_KEYS:
            if k not in ("tipo_documento", "fecha_emision", "moneda"):
                trace[k] = _trace(tipo_doc, "anexo_skip_campo", [])
        return fields, trace

    if tipo_doc == "informe_comision":
        fields["tipo_documento"] = "informe_comision"
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        fe, fer, fel = _fecha_informe_comision(text)
        if fe:
            fields["fecha_emision"] = fe
            trace["fecha_emision"] = _trace(tipo_doc, fer, fel)
        for k in _FIELD_KEYS:
            if k not in ("tipo_documento", "fecha_emision", "moneda"):
                trace[k] = _trace(tipo_doc, "informe_sin_campo_extra", [])
        return fields, trace

    if tipo_doc == "factura":
        fields["tipo_documento"] = "01"
        head, body = _factura_split_head_body(text)
        ruc_em, ruc_rec, ruc_lines = _factura_rucs(head, body)
        fields["ruc_emisor"] = ruc_em
        fields["ruc_receptor"] = ruc_rec
        trace["ruc_emisor"] = _trace(tipo_doc, "factura_ruc_header", ruc_lines[:2])
        trace["ruc_receptor"] = _trace(tipo_doc, "factura_ruc_cliente", ruc_lines[2:4])

        ser, sreg, slines = _factura_serie(text, head)
        fields["serie_numero"] = ser
        trace["serie_numero"] = _trace(tipo_doc, sreg, slines)

        rz, rz_reg, rz_lines = _factura_razon_social(head)
        fields["razon_social_emisor"] = rz
        trace["razon_social_emisor"] = _trace(tipo_doc, rz_reg, rz_lines)

        montos, mreg, mlines = _factura_montos(text)
        fields["monto_subtotal"] = montos["monto_subtotal"]
        fields["monto_igv"] = montos["monto_igv"]
        fields["monto_total"] = montos["monto_total"]
        trace["monto_subtotal"] = _trace(tipo_doc, mreg, mlines)
        trace["monto_igv"] = _trace(tipo_doc, mreg, mlines)
        trace["monto_total"] = _trace(tipo_doc, mreg, mlines)
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        return fields, trace

    if tipo_doc == "nota_pago":
        fields["tipo_documento"] = "nota_pago"
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        ns, ns_reg, ns_ln = _nota_serie(text)
        fields["serie_numero"] = ns
        trace["serie_numero"] = _trace(tipo_doc, ns_reg, ns_ln)
        ruc, rr, rl = _nota_ruc_emisor(text)
        fields["ruc_emisor"] = ruc
        trace["ruc_emisor"] = _trace(tipo_doc, rr, rl)
        mt: str | None = None
        mreg = "nota_total_none"
        mln: list[str] = []
        m = re.search(r"([\d]+[.,]\d{2})\s*\(\s*NOVECIENTOS", text, re.I)
        if m:
            mt = _norm_amount_str(m.group(1))
            mreg = "nota_total_monto_letras_novecientos"
            mln = [m.group(0)[:120]]
        if not mt:
            m = re.search(r"Total\s+a\s+pagar\s*:?\s*S/?\.?\s*([\d]+[.,]\d{2})", text, re.I)
            if m:
                mt = _norm_amount_str(m.group(1))
                mreg = "nota_total_etiqueta"
                mln = [m.group(0).strip()]
        if not mt:
            m = re.search(r"S/?\.?\s*([\d]+[.,]\d{2})\s*\(\s*NOVECIENTOS", text, re.I)
            if m:
                mt = _norm_amount_str(m.group(1))
                mreg = "nota_total_s_monto_letras"
                mln = [m.group(0)[:120]]
        fields["monto_total"] = mt
        trace["monto_total"] = _trace(tipo_doc, mreg, mln)
        for k in ("monto_subtotal", "monto_igv", "ruc_receptor", "razon_social_emisor"):
            trace[k] = _trace(tipo_doc, "nota_no_extraido", [])
        return fields, trace

    if tipo_doc in ("planilla_viaticos", "solicitud_viaticos"):
        td = "planilla_viaticos" if tipo_doc == "planilla_viaticos" else "solicitud_viaticos"
        fields["tipo_documento"] = td
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        ss, sr, sln = _planilla_solicitud_serie(text, tipo_doc)
        fields["serie_numero"] = ss
        trace["serie_numero"] = _trace(tipo_doc, sr, sln)
        ruc, rr, rl = _planilla_solicitud_ruc(text)
        fields["ruc_emisor"] = ruc
        trace["ruc_emisor"] = _trace(tipo_doc, rr, rl)
        if tipo_doc == "planilla_viaticos":
            mt, mr, mln = _planilla_monto_total(text)
            fields["monto_total"] = mt
            trace["monto_total"] = _trace(tipo_doc, mr, mln)
        for k in ("monto_subtotal", "monto_igv", "ruc_receptor"):
            trace[k] = _trace(tipo_doc, "planilla_sol_no_campo", [])
        # razón: comisionado
        m = re.search(r"Sr\(a\):\s*([^\n]+)", text, re.I)
        if m:
            fields["razon_social_emisor"] = m.group(1).strip()[:120]
            trace["razon_social_emisor"] = _trace(tipo_doc, "planilla_sra_comisionado", [m.group(0).strip()])
        elif tipo_doc == "planilla_viaticos":
            m2 = re.search(r"AMIQUERO[^\n]+", text, re.I)
            if m2:
                fields["razon_social_emisor"] = m2.group(0).strip()[:120]
                trace["razon_social_emisor"] = _trace(tipo_doc, "planilla_nombre_matcher", [m2.group(0).strip()])
        return fields, trace

    if tipo_doc == "ri":
        fields["tipo_documento"] = "ri"
        trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
        r, rr, rl = _ri_ruc(text)
        fields["ruc_emisor"] = r
        trace["ruc_emisor"] = _trace(tipo_doc, rr, rl)
        s, sr, sl = _ri_serie(text)
        fields["serie_numero"] = s
        trace["serie_numero"] = _trace(tipo_doc, sr, sl)
        mt, mtr, ml = _ri_monto_total(text)
        fields["monto_total"] = mt
        trace["monto_total"] = _trace(tipo_doc, mtr, ml)
        for k in ("monto_subtotal", "monto_igv", "ruc_receptor", "razon_social_emisor"):
            trace[k] = _trace(tipo_doc, "ri_no_campo", [])
        return fields, trace

    # desconocido: fallback tipo mínimo parecido a extractores sueltos
    fields["tipo_documento"] = None
    trace["tipo_documento"] = _trace(tipo_doc, regla_tipo, [])
    rucs = _find_rucs_with_context(text)
    if rucs:
        fields["ruc_emisor"] = rucs[0][0]
        trace["ruc_emisor"] = _trace(tipo_doc, "fallback_primer_ruc", [rucs[0][1]])
    return fields, trace


def field_keys() -> list[str]:
    return list(_FIELD_KEYS)
