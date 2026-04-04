"""Normaliza la entrada y registra el paso en el historial."""

from __future__ import annotations

from dataclasses import replace

from state import AgentState


def input_node(state: AgentState) -> AgentState:
    texto = (state.input_usuario or "").strip()
    s = replace(state, input_usuario=texto)
    if not texto:
        return replace(
            s,
            error_flujo="entrada_vacia",
            historial=s.historial + ("input_node: vacío",),
        )
    return s.with_append_historial(f"input_node: recibido ({len(texto)} caracteres)")
