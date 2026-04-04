"""Validación del envelope devuelto por tools (listo para políticas MINEDU)."""

from __future__ import annotations

from dataclasses import replace

from state import AgentState

_CAMPOS_REQUERIDOS = frozenset({"ok", "tool", "message", "data"})


def _schema_valido(resultado: dict) -> bool:
    return all(k in resultado for k in _CAMPOS_REQUERIDOS)


def _buscar_pdf_con_resultados(resultado: dict) -> bool:
    """Exige payload con fragmentos cuando la tool es buscar_en_pdf."""
    if resultado.get("tool") != "buscar_en_pdf":
        return True
    if not resultado.get("ok"):
        return False
    data = resultado.get("data")
    return isinstance(data, list) and len(data) > 0


def validation_node(state: AgentState) -> AgentState:
    if state.error_flujo:
        return state.with_append_historial("validation_node: omitido (error previo)")

    if state.tool_seleccionado is None:
        s = replace(state, validacion_ok=True)
        return s.with_append_historial("validation_node: sin tool — sin validar payload")

    if state.resultado_tool is None:
        s = replace(state, validacion_ok=False)
        return s.with_append_historial("validation_node: falla — ejecución sin resultado")

    esquema = _schema_valido(state.resultado_tool)
    ok = esquema
    if ok and state.tool_seleccionado == "buscar_en_pdf":
        ok = _buscar_pdf_con_resultados(state.resultado_tool)

    if state.tool_seleccionado == "buscar_en_pdf":
        if not esquema:
            msg_hist = "validation_node: esquema inválido"
        elif not ok:
            msg_hist = "validation_node: buscar_en_pdf sin fragmentos válidos (fallback)"
        else:
            msg_hist = "validation_node: buscar_en_pdf con fragmentos"
    else:
        msg_hist = f"validation_node: esquema {'válido' if esquema else 'inválido'}"

    s = replace(state, validacion_ok=ok)
    return s.with_append_historial(msg_hist)
