"""
Orquestador: grafo con ciclo acotado (máx. 2 vueltas) en el tramo decisión→acción→validación.

input → [ reasoning → tool → validación ] * (≤2) → output

Misma topología de nodos; el bucle solo repite el trazo cuando la validación falla y hay tool.
"""

from __future__ import annotations

from dataclasses import replace

from nodes import (
    input_node,
    output_node,
    reasoning_node,
    tool_node,
    validation_node,
)
from state import AgentState

_MAX_CICLOS_DECISION = 2


def _mensaje_reintento(estado: AgentState) -> str:
    if estado.tool_seleccionado == "buscar_en_pdf":
        rt = estado.resultado_tool if isinstance(estado.resultado_tool, dict) else {}
        if not rt:
            return "Validación: buscar_en_pdf sin resultado; reintento con misma herramienta."
        data = rt.get("data")
        if rt.get("ok") and isinstance(data, list) and len(data) == 0:
            return (
                "Validación: buscar_en_pdf sin fragmentos; reintento controlado "
                "(misma consulta, segunda pasada determinista)."
            )
        if rt.get("ok") is False:
            return (
                "Validación: buscar_en_pdf devolvió ok=false; reintento controlado "
                "con la misma herramienta."
            )
    if not isinstance(estado.resultado_tool, dict):
        return "Validación: resultado de tool ausente o no dict; reintento controlado."
    faltan = {"ok", "tool", "message", "data"} - set(estado.resultado_tool.keys())
    if faltan:
        return f"Validación: envelope incompleto {sorted(faltan)}; reintento controlado."
    return "Validación: criterios no cumplidos tras ejecutar la herramienta; reintento controlado."


def run_pipeline(estado_inicial: AgentState) -> AgentState:
    estado = input_node(estado_inicial)
    if estado.error_flujo:
        estado = reasoning_node(estado)
        estado = tool_node(estado)
        estado = validation_node(estado)
        return output_node(estado)

    for indice_ciclo in range(_MAX_CICLOS_DECISION):
        estado = replace(estado, ciclo_decision=indice_ciclo)
        estado = reasoning_node(estado)
        estado = tool_node(estado)
        estado = validation_node(estado)

        if estado.validacion_ok:
            estado = replace(estado, retroalimentacion_validacion=None)
            break

        if not estado.tool_seleccionado:
            break

        if indice_ciclo >= _MAX_CICLOS_DECISION - 1:
            break

        estado = replace(
            estado,
            retroalimentacion_validacion=_mensaje_reintento(estado),
            resultado_tool=None,
        )

    return output_node(estado)
