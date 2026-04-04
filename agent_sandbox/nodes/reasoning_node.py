"""Clasificación de intención: LLM una sola vez por turno; reintentos sin LLM adicional."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from llm_client import analizar_con_llm, tiene_intencion_normativa
from state import AgentState


def _fase_analisis_intencion(state: AgentState) -> dict[str, Any]:
    """
    a) Análisis de intención.
    Una sola llamada al clasificador LLM salvo que ya exista retroalimentación de validación
    (segundo ciclo: decisión determinista, sin LLM adicional).
    """
    if state.retroalimentacion_validacion:
        tool_prev = state.tool_seleccionado
        if not tool_prev:
            return {
                "intencion": state.intencion or "reintento_sin_tool",
                "tool": None,
                "confianza": 0.3,
                "fuente": "reintento_determinista_sin_tool",
                "retroalimentacion_aplicada": state.retroalimentacion_validacion,
            }
        return {
            "intencion": state.intencion or "reintento_controlado",
            "tool": tool_prev,
            "confianza": 0.88,
            "fuente": "reintento_determinista",
            "retroalimentacion_aplicada": state.retroalimentacion_validacion,
        }

    return analizar_con_llm(state.input_usuario)


def _fase_decision_accion(
    resultado: dict[str, Any],
    state: AgentState,
) -> dict[str, Any]:
    """
    b) Decisión explícita: usar tool. Si el clasificador no propone tool → RAG por defecto.
    """
    tool = resultado.get("tool")
    if tool:
        just = (
            f"Ejecutar herramienta '{tool}' (fuente={resultado.get('fuente')}, "
            f"ciclo={state.ciclo_decision}). "
            f"Intención: {resultado.get('intencion')!r}."
        )
        if resultado.get("retroalimentacion_aplicada"):
            just += f" Contexto validación: {resultado['retroalimentacion_aplicada']!r}."
        return {"type": "tool", "tool_name": tool, "justification": just}

    just = (
        "fallback por defecto a RAG (buscar_en_pdf); clasificación sin tool "
        f"(fuente={resultado.get('fuente')}, ciclo={state.ciclo_decision}). "
        f"Intención: {resultado.get('intencion')!r}."
    )
    if resultado.get("retroalimentacion_aplicada"):
        just += f" Contexto validación: {resultado['retroalimentacion_aplicada']!r}."
    return {
        "type": "tool",
        "tool_name": "buscar_en_pdf",
        "justification": just,
    }


def _fase_preparacion_siguiente_paso(
    state: AgentState,
    resultado: dict[str, Any],
    next_action: dict[str, Any],
) -> AgentState:
    """c) Volcar decisión en campos que consumen tool_node y el resto del grafo."""
    tool_nom: str | None = None
    if next_action.get("type") == "tool":
        tn = next_action.get("tool_name")
        tool_nom = str(tn) if tn else None

    return replace(
        state,
        intencion=resultado.get("intencion"),
        tool_seleccionado=tool_nom,
        next_action=dict(next_action),
    )


def reasoning_node(state: AgentState) -> AgentState:
    if state.error_flujo:
        return state.with_append_historial(
            "reasoning_node: omitido (error en entrada)"
        )

    resultado = _fase_analisis_intencion(state)
    next_action = _fase_decision_accion(resultado, state)
    rag_fallback_default = (
        next_action.get("type") == "tool"
        and next_action.get("tool_name") == "buscar_en_pdf"
        and not resultado.get("tool")
    )
    s = _fase_preparacion_siguiente_paso(state, resultado, next_action)

    evento_auditoria: dict[str, Any] = {
        "nodo": "reasoning",
        "fase": "analisis_decision_preparacion",
        "ciclo_decision": state.ciclo_decision,
        "input": state.input_usuario,
        "intencion": resultado.get("intencion"),
        "tool": resultado.get("tool"),
        "next_action": dict(next_action),
        "confianza": resultado.get("confianza"),
        "fuente": resultado.get("fuente"),
        "rag_fallback_default": rag_fallback_default,
    }
    for clave_extra in (
        "motivo_fallback",
        "confianza_llm_rechazada",
        "intencion_llm_previa",
        "tool_llm_previo",
        "retroalimentacion_aplicada",
    ):
        if clave_extra in resultado:
            evento_auditoria[clave_extra] = resultado[clave_extra]

    if tiene_intencion_normativa(state.input_usuario):
        evento_auditoria["senales_normativas"] = True

    s = s.with_traza_decision(evento_auditoria)

    tool_log = next_action.get("tool_name") or resultado.get("tool") or "null"
    resumen = (
        f"reasoning_node: ciclo={state.ciclo_decision} "
        f"accion={next_action.get('type')} "
        f"fuente={resultado.get('fuente')} "
        f"tool_efectiva={tool_log}"
        + (" [rag_fallback]" if rag_fallback_default else "")
    )
    return s.with_append_historial(resumen)
