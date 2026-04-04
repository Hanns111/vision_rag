"""Estado compartido del agente (mutable solo a través de nodos)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


def _copiar_evento_auditoria(d: dict[str, Any]) -> dict[str, Any]:
    return dict(d)


@dataclass(frozen=True)
class AgentState:
    """
    Snapshot inmutable del ciclo del agente.
    Los nodos devuelven un nuevo AgentState vía dataclasses.replace.
    """

    input_usuario: str
    intencion: str | None = None
    tool_seleccionado: str | None = None
    resultado_tool: dict[str, Any] | None = None
    respuesta_final: str | None = None
    historial: tuple[str, ...] = field(default_factory=tuple)
    """Bitácora legible (nodos legacy)."""
    trazas_decision: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    """Eventos estructurados para auditoría (p. ej. razonamiento LLM)."""
    validacion_ok: bool | None = None
    error_flujo: str | None = None
    #: Decisión explícita del ciclo (patrón decide → actuar → validar).
    next_action: dict[str, Any] | None = None
    #: Texto de contexto cuando validation solicita un segundo paso de razonamiento (sin LLM extra).
    retroalimentacion_validacion: str | None = None
    #: Índice del ciclo razonamiento→tool→validación (0-based; máx. 2 ciclos en orquestador).
    ciclo_decision: int = 0

    def with_append_historial(self, entrada: str) -> AgentState:
        return replace(self, historial=self.historial + (entrada,))

    def with_traza_decision(self, evento: dict[str, Any]) -> AgentState:
        return replace(
            self,
            trazas_decision=self.trazas_decision + (_copiar_evento_auditoria(evento),),
        )

    @staticmethod
    def desde_entrada(texto: str) -> AgentState:
        return AgentState(input_usuario=texto or "")
