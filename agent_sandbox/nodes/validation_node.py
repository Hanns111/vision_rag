"""Validación del flujo post-tool (política permisiva: consulta no vacía)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from state import AgentState

_CAMPOS_REQUERIDOS = frozenset({"ok", "tool", "message", "data"})


def _schema_valido(resultado: dict) -> bool:
    return all(k in resultado for k in _CAMPOS_REQUERIDOS)


def _buscar_pdf_con_resultados(resultado: dict) -> bool:
    """Diagnóstico: ¿payload con fragmentos cuando la tool es buscar_en_pdf?"""
    if resultado.get("tool") != "buscar_en_pdf":
        return True
    if not resultado.get("ok"):
        return False
    data = resultado.get("data")
    return isinstance(data, list) and len(data) > 0


def validation_node(state: AgentState) -> AgentState:
    if state.error_flujo:
        return state.with_append_historial("validation_node: omitido (error previo)")

    query = (state.input_usuario or "").strip()
    validacion_ok = len(query) > 5

    ev_val: dict[str, Any] = {
        "nodo": "validation",
        "ok": validacion_ok,
        "ciclo_decision": state.ciclo_decision,
        "longitud_consulta": len(query),
        "regla": "consulta_no_vacia_gt_5",
    }
    if not validacion_ok:
        ev_val["motivo"] = "consulta_muy_corta_o_vacia"

    if state.tool_seleccionado is not None:
        ev_val["tool"] = state.tool_seleccionado
        if state.resultado_tool is not None:
            esquema = _schema_valido(state.resultado_tool)
            ev_val["esquema_payload"] = esquema
            if state.tool_seleccionado == "buscar_en_pdf":
                ev_val["fragmentos_pdf_ok"] = _buscar_pdf_con_resultados(
                    state.resultado_tool
                )
        else:
            ev_val["sin_resultado_tool"] = True
    else:
        ev_val["sin_tool"] = True

    if validacion_ok:
        if state.tool_seleccionado is None:
            msg_hist = "validation_node: sin tool — consulta aceptada (len>5)"
        else:
            msg_hist = (
                f"validation_node: consulta aceptada (len={len(query)}); "
                f"tool={state.tool_seleccionado!r} (sin bloqueo por payload)"
            )
    else:
        msg_hist = f"validation_node: consulta rechazada — muy corta o vacía (len={len(query)})"

    s = replace(state, validacion_ok=validacion_ok)
    s = s.with_traza_decision(ev_val)
    return s.with_append_historial(msg_hist)
