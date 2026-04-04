"""Construye la respuesta final (presentación; la lógica de negocio vive en tools)."""

from __future__ import annotations

from dataclasses import replace

from agent_audit_log import (
    append_run_record,
    decision_summary_for_display,
    show_decision_in_output,
)
from state import AgentState


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
        partes = [msg, "", "Resultados (RAG semántico):"]
        for i, fr in enumerate(raw_data, 1):
            if not isinstance(fr, dict):
                continue
            sc = fr.get("score", fr.get("similitud", 0))
            arch = fr.get("archivo", "?")
            pi = fr.get("pagina")
            pf = fr.get("pagina_fin", pi)
            if pi is None:
                pag = "p.?"
            elif pf is not None and pf != pi:
                pag = f"p.{pi}-{pf}"
            else:
                pag = f"p.{pi}"
            conf = fr.get("confidence")
            cid = fr.get("chunk_id", "")
            extra = ""
            if conf is not None:
                extra += f" conf={conf}"
            if cid:
                extra += f" id={cid}"
            tchunk = fr.get("tipo")
            if tchunk:
                extra += f" tipo={tchunk}"
            cab = f"[{i}] (score={sc}) {arch} {pag}{extra}"
            citas_partes: list[str] = []
            if fr.get("articulo"):
                citas_partes.append(str(fr["articulo"]))
            if fr.get("numeral"):
                citas_partes.append(str(fr["numeral"]))
            if fr.get("inciso"):
                citas_partes.append(str(fr["inciso"]))
            linea_citas = " – ".join(citas_partes) if citas_partes else ""
            txt = (fr.get("texto") or "").strip()
            bloque = [f"\n{cab}"]
            if linea_citas:
                bloque.append(linea_citas)
            bloque.append(f'"{txt}"')
            partes.append("\n".join(bloque))
        linea = "\n".join(partes).strip()
    else:
        linea = msg

    cuerpo = linea.strip()
    s = replace(state, respuesta_final=_concat_respuesta(cuerpo, state))
    s = s.with_append_historial("output_node: respuesta final lista")
    append_run_record(s, cuerpo)
    return s
