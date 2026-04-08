"""Construye la respuesta final (presentación; la lógica de negocio vive en tools)."""

from __future__ import annotations

import os
import re
from dataclasses import replace

from agent_audit_log import (
    append_run_record,
    decision_summary_for_display,
    show_decision_in_output,
)
from state import AgentState

# Heurísticas léxicas sobre texto ya recuperado (sin LLM). Orden: más específicas primero.
_PATRONES_IDEA_CLAVE = (
    r"no\s+debe\s+exceder(?:\s+del)?[^.]{0,450}\.",
    r"no\s+puede\s+exceder(?:\s+del)?[^.]{0,450}\.",
    r"hasta\s+por\s+un\s+monto[^.]{0,450}\.",
    r"se\s+establece(?:\s+que)?[^.]{0,450}\.",
    r"(?:^|[\n.;]\s*)(?:corresponde|corresponden)[^.]{0,450}\.",
    r"[^.]{0,120}(?:treinta\s+por\s+ciento|\d{1,3}\s*\%)[^.]{0,400}\.",
    r"S/\s*[\d.,]+\s*(?:\([^)]{0,80}\))?[^.]{0,280}\.",
    r"(?:monto|montos|tope|l[ií]mite)[^.]{0,350}\.",
)


def _normalizar_espacios(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _fragmento_inicial_limpio(texto: str, lim: int = 400) -> str:
    """Si no hay patrón claro: primer tramo del texto recuperado, sin inventar."""
    t = _normalizar_espacios(texto)
    if not t:
        return ""
    if len(t) <= lim:
        return t
    corte = t[: lim + 1]
    if " " in corte:
        corte = corte[: lim].rsplit(" ", 1)[0]
    return corte.rstrip(",;:") + "…"


def _extraer_idea_clave_desde_texto(texto: str, max_len: int = 520) -> str:
    t = texto or ""
    for patron in _PATRONES_IDEA_CLAVE:
        m = re.search(patron, t, re.IGNORECASE | re.MULTILINE)
        if m:
            frag = _normalizar_espacios(m.group(0))
            if len(frag) >= 25:
                return frag[:max_len] + ("…" if len(frag) > max_len else "")
    return ""


def _formatear_rango_pagina(pi: object, pf: object) -> str:
    if pi is None:
        return "?"
    if pf is not None and pf != pi:
        return f"{pi}-{pf}"
    return str(pi)


def _es_texto_legible(texto: str) -> bool:
    """Sanidad superficial del extracto (no sustituye verificación jurídica del PDF)."""
    if not texto:
        return False
    alnum = sum(c.isalnum() for c in texto)
    ratio = alnum / max(len(texto), 1)
    raros = sum(1 for c in texto if c in "|~¤")
    raro_ratio = raros / max(len(texto), 1)
    return len(texto) >= 40 and ratio > 0.7 and raro_ratio < 0.1


def _modo_salida_rag() -> str:
    """short = adaptativo; verbose|debug|full = salida completa (histórica)."""
    m = (os.getenv("AGENT_OUTPUT_MODE") or "short").strip().lower()
    if m in ("verbose", "debug", "full"):
        return "verbose"
    return "short"


def _format_rag_verbose(
    msg: str,
    fr: dict[str, object],
    frags: list[dict[str, object]],
    texto_full: str,
) -> str:
    respuesta = _extraer_idea_clave_desde_texto(texto_full) or _fragmento_inicial_limpio(
        texto_full
    )
    arch = fr.get("archivo", "?")
    pi = fr.get("pagina")
    pf = fr.get("pagina_fin", pi)
    pag = _formatear_rango_pagina(pi, pf)
    cid = fr.get("chunk_id", "")
    conf = fr.get("confidence")

    bloques: list[str] = [
        msg,
        "",
        "Respuesta:",
        "",
        respuesta,
        "",
        "Fuente:",
        f"{arch} - página {pag}",
    ]
    if cid:
        bloques.append(f"chunk_id: {cid}")
    if conf is not None:
        bloques.append(f"confidence: {conf}")

    lim_completo = 2400
    tf = texto_full
    bloques.extend(
        [
            "",
            "---",
            "Texto del fragmento principal (recuperado, sin reinterpretar):",
            (
                tf
                if len(tf) <= lim_completo
                else tf[: lim_completo - 1].rsplit(" ", 1)[0] + "…"
            ),
        ]
    )
    if len(frags) > 1:
        bloques.extend(["", "Otros fragmentos recuperados (resumen):"])
        for i, otro in enumerate(frags[1:], start=2):
            sc = otro.get("score", otro.get("similitud", 0))
            a = otro.get("archivo", "?")
            p_i = otro.get("pagina")
            p_f = otro.get("pagina_fin", p_i)
            pags = _formatear_rango_pagina(p_i, p_f)
            tip = otro.get("tipo", "")
            suf = f" tipo={tip}" if tip else ""
            bloques.append(f"  [{i}] score={sc} {a} p.{pags}{suf}")
    return "\n".join(bloques).strip()


def _format_rag_adaptive(fr: dict[str, object], texto_full: str) -> str:
    idea = _extraer_idea_clave_desde_texto(texto_full)
    fragmento = _fragmento_inicial_limpio(texto_full)
    idea_valida = bool(idea) and _es_texto_legible(idea)
    fragmento_valido = bool(fragmento) and _es_texto_legible(fragmento)
    arch = fr.get("archivo", "?")
    pi = fr.get("pagina")
    pf = fr.get("pagina_fin", pi)
    fuente_line = f"{arch} - página {_formatear_rango_pagina(pi, pf)}"

    if idea_valida:
        salida = f"Respuesta: {idea}\nFuente: {fuente_line}"
        if not fragmento_valido:
            frag_extra = (fragmento or texto_full[:400]).strip()
            if frag_extra:
                salida += f"\n\nFragmento:\n{frag_extra}"
        return salida
    if fragmento_valido:
        return f"Fuente: {fuente_line}\n\nFragmento:\n{fragmento}"
    fallback = (texto_full[:400] if texto_full else "").strip()
    if not fallback:
        fallback = "(sin texto recuperado en el chunk)"
    return f"Fuente: {fuente_line}\n\nTexto:\n{fallback}"


def _concat_respuesta(cuerpo: str, state: AgentState) -> str:
    cuerpo = (cuerpo or "").strip()
    if not show_decision_in_output():
        return cuerpo
    bloque = decision_summary_for_display(state)
    if not bloque:
        return cuerpo
    if not cuerpo:
        return bloque
    return f"{cuerpo}\n\n{bloque}"


def output_node(state: AgentState) -> AgentState:
    if state.error_flujo == "entrada_vacia":
        cuerpo = "Escribe una consulta."
        s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
        s = s.with_append_historial("output_node: respuesta entrada vacía")
        append_run_record(s, cuerpo)
        return s

    if state.validacion_ok is False:
        rt = state.resultado_tool if isinstance(state.resultado_tool, dict) else {}
        if state.tool_seleccionado == "buscar_en_pdf" and rt.get("message"):
            cuerpo = str(rt.get("message"))
        else:
            cuerpo = "[Sistema] La herramienta devolvió un resultado inválido."
        s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
        s = s.with_append_historial("output_node: fallo de validación / sin fragmentos")
        append_run_record(s, cuerpo)
        return s

    if not state.tool_seleccionado:
        cuerpo = (
            "No reconozco la intención. Incluye, por ejemplo: "
            "'ruc', 'pdf', 'monto', o términos normativos (norma, directiva, artículo, viáticos)."
        )
        s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
        s = s.with_append_historial("output_node: intención desconocida")
        append_run_record(s, cuerpo)
        return s

    res = state.resultado_tool or {}
    msg = res.get("message", "")
    raw_data = res.get("data")
    data = raw_data if isinstance(raw_data, dict) else {}

    if not res.get("ok"):
        cuerpo = msg or ""
        s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
        s = s.with_append_historial("output_node: resultado de negocio no exitoso")
        append_run_record(s, cuerpo)
        return s

    tool = state.tool_seleccionado
    if tool == "validar_ruc":
        ruc = data.get("ruc")
        linea = f"{msg} (RUC: {ruc})"
    elif tool == "leer_pdf":
        extra = data.get("contenido_simulado", "")
        linea = f"{msg} Archivo: {data.get('ruta')}. Extracto: {extra}"
    elif tool == "calcular_monto":
        linea = (
            f"{msg} Total: {data.get('total')} (detalle: {data.get('valores')})"
        )
    elif tool == "buscar_en_pdf" and isinstance(raw_data, list):
        frags = [f for f in raw_data if isinstance(f, dict)]
        frags.sort(key=lambda x: float(x.get("score", 0) or 0), reverse=True)
        if not frags:
            linea = msg
        else:
            fr = frags[0]
            texto_full = (fr.get("texto") or "").strip()
            if _modo_salida_rag() == "verbose":
                linea = _format_rag_verbose(msg, fr, frags, texto_full)
            else:
                linea = _format_rag_adaptive(fr, texto_full)
    else:
        linea = msg

    cuerpo = linea.strip()
    s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
    s = s.with_append_historial("output_node: respuesta final lista")
    append_run_record(s, cuerpo)
    return s
