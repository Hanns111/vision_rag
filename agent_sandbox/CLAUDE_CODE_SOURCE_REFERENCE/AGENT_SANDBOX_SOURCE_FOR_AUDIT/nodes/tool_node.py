"""Ejecución de la herramienta elegida."""

from __future__ import annotations

from dataclasses import replace

import tools
from state import AgentState


def tool_node(state: AgentState) -> AgentState:
    if state.error_flujo:
        return state.with_append_historial("tool_node: omitido (error previo)")

    if not state.tool_seleccionado:
        s = replace(state, resultado_tool=None)
        return s.with_append_historial("tool_node: sin tool; no se ejecuta nada")

    resultado = tools.despachar(state.tool_seleccionado, state.input_usuario)
    s = replace(state, resultado_tool=resultado)
    return s.with_append_historial(
        f"tool_node: ejecutado {state.tool_seleccionado} ok={resultado.get('ok')}"
    )
