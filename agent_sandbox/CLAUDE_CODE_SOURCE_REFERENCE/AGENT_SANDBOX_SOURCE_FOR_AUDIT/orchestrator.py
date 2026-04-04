"""
Orquestador: grafo lineal de nodos (equivalente conceptual a LangGraph sin dependencias).

input → reasoning → tool → validation → output
"""

from __future__ import annotations

from collections.abc import Callable

from nodes import (
    input_node,
    output_node,
    reasoning_node,
    tool_node,
    validation_node,
)
from state import AgentState

Nodo = Callable[[AgentState], AgentState]

PIPELINE: tuple[Nodo, ...] = (
    input_node,
    reasoning_node,
    tool_node,
    validation_node,
    output_node,
)


def run_pipeline(estado_inicial: AgentState) -> AgentState:
    estado = estado_inicial
    for nodo in PIPELINE:
        estado = nodo(estado)
    return estado
