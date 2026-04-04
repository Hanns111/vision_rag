"""Clasificación de intención: LLM validado, trazable y con fallback a reglas."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from llm_client import analizar_con_llm, tiene_intencion_normativa
from state import AgentState


def reasoning_node(state: AgentState) -> AgentState:
    if state.error_flujo:
        return state.with_append_historial(
            "reasoning_node: omitido (error en entrada)"
        )

    resultado = analizar_con_llm(state.input_usuario)

    evento_auditoria: dict[str, Any] = {
        "nodo": "reasoning",
        "input": state.input_usuario,
        "intencion": resultado["intencion"],
        "tool": resultado["tool"],
        "confianza": resultado["confianza"],
        "fuente": resultado["fuente"],
    }
    for clave_extra in (
        "motivo_fallback",
        "confianza_llm_rechazada",
        "intencion_llm_previa",
        "tool_llm_previo",
    ):
        if clave_extra in resultado:
            evento_auditoria[clave_extra] = resultado[clave_extra]

    if tiene_intencion_normativa(state.input_usuario):
        evento_auditoria["senales_normativas"] = True

    s = replace(
        state,
        intencion=resultado["intencion"],
        tool_seleccionado=resultado["tool"],
    )
    s = s.with_traza_decision(evento_auditoria)

    resumen = (
        f"reasoning_node: fuente={resultado['fuente']} "
        f"conf={resultado['confianza']:.2f} "
        f"tool={resultado['tool'] or 'null'}"
    )
    return s.with_append_historial(resumen)
