"""Persistencia append-only de ejecuciones del agente (JSONL, auditable)."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from state import AgentState

_LOGGER = logging.getLogger(__name__)

_LOG_DIR = Path(__file__).resolve().parent / "logs"
_LOG_FILE = _LOG_DIR / "agent_log.jsonl"


def _snap_reasoning(state: AgentState) -> dict[str, Any]:
    for ev in reversed(state.trazas_decision):
        if ev.get("nodo") == "reasoning":
            return dict(ev)
    return {
        "input": state.input_usuario,
        "intencion": state.intencion,
        "tool": state.tool_seleccionado,
        "confianza": None,
        "fuente": "sin_traza",
    }


def _fallback_flag(snap: dict[str, Any], fuente: str) -> bool:
    if fuente == "fallback_reglas":
        return True
    if snap.get("motivo_fallback"):
        return True
    return False


def append_run_record(state: AgentState, resultado_limpio: str) -> None:
    """
    Añade una línea JSON al log. No sobrescribe el archivo; errores de I/O se registran y no propagan.
    """
    snap = _snap_reasoning(state)
    fuente = str(snap.get("fuente") or "desconocido")
    conf = snap.get("confianza")
    if conf is not None and not isinstance(conf, (int, float)):
        try:
            conf = float(conf)
        except (TypeError, ValueError):
            conf = None

    tool_val = snap.get("tool")
    if tool_val is None and state.tool_seleccionado is not None:
        tool_val = state.tool_seleccionado

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": state.input_usuario or "",
        "intencion": snap.get("intencion") or state.intencion or "",
        "tool": tool_val,
        "confianza": conf,
        "fuente": fuente,
        "resultado": resultado_limpio or "",
        "fallback": _fallback_flag(snap, fuente),
    }

    line = json.dumps(record, ensure_ascii=False) + "\n"

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_LOG_FILE, "a", encoding="utf-8", newline="\n") as f:
            f.write(line)
    except OSError as exc:
        _LOGGER.warning("No se pudo escribir %s: %s", _LOG_FILE, exc)


def decision_summary_for_display(state: AgentState) -> str | None:
    """Texto multilínea para mostrar al usuario, o None si no hay traza de reasoning."""
    for ev in reversed(state.trazas_decision):
        if ev.get("nodo") != "reasoning":
            continue
        intencion = ev.get("intencion", "")
        tool = ev.get("tool")
        tool_s = tool if tool is not None else "null"
        conf = ev.get("confianza")
        conf_s = f"{float(conf):.2f}" if isinstance(conf, (int, float)) else str(conf)
        fuente = ev.get("fuente", "")
        na = ev.get("next_action")
        bloque_na = ""
        if isinstance(na, dict):
            j = na.get("justification")
            t = na.get("type")
            if j or t:
                bloque_na = (
                    f"\n* next_action.type: {t}\n"
                    f"* justificación: {j or '(sin texto)'}"
                )
        ciclo = ev.get("ciclo_decision")
        sufijo_ciclo = ""
        if ciclo is not None:
            sufijo_ciclo = f"\n* ciclo_decision: {ciclo}"
        return (
            "Decisión:\n\n"
            f"* intención: {intencion}\n"
            f"* tool: {tool_s}\n"
            f"* confianza: {conf_s}\n"
            f"* fuente: {fuente}"
            f"{sufijo_ciclo}"
            f"{bloque_na}"
        )
    return None


def show_decision_in_output() -> bool:
    v = (os.environ.get("AGENT_SHOW_DECISION_SUMMARY") or "").strip().lower()
    return v in ("1", "true", "yes", "on", "si", "sí")
