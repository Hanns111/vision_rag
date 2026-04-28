"""
Modelo de salida del motor PASO 4.5 — schema `decision_engine.v1`.

Dataclasses puras, sin lógica de reglas. Cada `to_dict()` produce
estructuras JSON-serializables con orden de claves explícito. La
`metadata_corrida` (timestamps, run_id, host, git_commit) se mantiene
separada para que `to_dict_deterministic()` excluya ese sub-objeto y
permita comparaciones byte-a-byte byte-a-byte sobre el mismo input
(regla 6 del PASO 4.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SCHEMA_VERSION = "decision_engine.v1"
ENGINE_VERSION = "0.1.0"
RULESET_VERSION = "v1-mvp"


# Resultado de una regla o hallazgo.
RESULTADO_OK = "OK"
RESULTADO_OBSERVAR = "OBSERVAR"
RESULTADO_REVISAR = "REVISAR"
RESULTADO_NO_APLICABLE = "NO_APLICABLE"

RESULTADOS_VALIDOS = (
    RESULTADO_OK,
    RESULTADO_OBSERVAR,
    RESULTADO_REVISAR,
    RESULTADO_NO_APLICABLE,
)

# Severidad opcional (ortogonal al resultado): prioriza la cola humana.
# La agregación a `decision_global` ignora `severidad` — solo mira `resultado`.
SEVERIDAD_BAJA = "BAJA"
SEVERIDAD_MEDIA = "MEDIA"
SEVERIDAD_ALTA = "ALTA"

SEVERIDADES_VALIDAS = (SEVERIDAD_BAJA, SEVERIDAD_MEDIA, SEVERIDAD_ALTA)

# Scope: qué objeto evalúa la regla.
SCOPE_EXPEDIENTE = "expediente"
SCOPE_COMPROBANTE = "comprobante"
SCOPE_DOCUMENTO = "documento"

SCOPES_VALIDOS = (SCOPE_EXPEDIENTE, SCOPE_COMPROBANTE, SCOPE_DOCUMENTO)


@dataclass
class Criterio:
    """Sub-criterio booleano evaluado dentro de una regla, con su valor."""
    criterio: str
    valor: Any
    ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterio": self.criterio,
            "valor": self.valor,
            "ok": self.ok,
        }


@dataclass
class Hallazgo:
    """Disparo concreto de una regla sobre un objeto. Plano para Fase 3 (UI)."""
    regla_id: str
    resultado: str                 # OBSERVAR | REVISAR (OK no genera hallazgo)
    severidad: str | None          # BAJA | MEDIA | ALTA | None
    scope: str                     # expediente | comprobante | documento
    objeto_id: str
    explicacion: str
    campos_implicados: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regla_id": self.regla_id,
            "resultado": self.resultado,
            "severidad": self.severidad,
            "scope": self.scope,
            "objeto_id": self.objeto_id,
            "explicacion": self.explicacion,
            "campos_implicados": list(self.campos_implicados),
        }


@dataclass
class ResultadoRegla:
    """Resultado de evaluar una regla sobre un objeto."""
    regla_id: str
    regla_version: str
    descripcion_corta: str
    scope: str
    severidad_max: str             # peor severidad que esta regla puede emitir
    resultado: str                 # OK | OBSERVAR | REVISAR | NO_APLICABLE
    severidad: str | None          # BAJA | MEDIA | ALTA | None
    objeto_evaluado_id: str
    evidencia_consultada: dict[str, Any] = field(default_factory=dict)
    criterios_evaluados: list[Criterio] = field(default_factory=list)
    explicacion: str = ""
    campos_implicados: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regla_id": self.regla_id,
            "regla_version": self.regla_version,
            "descripcion_corta": self.descripcion_corta,
            "scope": self.scope,
            "severidad_max": self.severidad_max,
            "resultado": self.resultado,
            "severidad": self.severidad,
            "objeto_evaluado_id": self.objeto_evaluado_id,
            "evidencia_consultada": dict(self.evidencia_consultada),
            "criterios_evaluados": [c.to_dict() for c in self.criterios_evaluados],
            "explicacion": self.explicacion,
            "campos_implicados": list(self.campos_implicados),
        }


@dataclass
class MetadataCorrida:
    """Datos no-deterministas de una ejecución (excluidos del diff de idempotencia)."""
    engine_run_id: str
    engine_run_timestamp_utc: str
    engine_host: str
    engine_git_commit: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine_run_id": self.engine_run_id,
            "engine_run_timestamp_utc": self.engine_run_timestamp_utc,
            "engine_host": self.engine_host,
            "engine_git_commit": self.engine_git_commit,
        }


@dataclass
class DecisionEngineOutput:
    """Salida completa del motor para un expediente."""
    expediente_id: str
    input_referenciado: dict[str, Any]
    decision_global: str           # OK | OBSERVAR | REVISAR
    resumen: dict[str, Any]
    reglas_evaluadas: list[ResultadoRegla] = field(default_factory=list)
    hallazgos: list[Hallazgo] = field(default_factory=list)
    metadata_corrida: MetadataCorrida | None = None
    schema_version: str = SCHEMA_VERSION
    engine_version: str = ENGINE_VERSION
    ruleset_version: str = RULESET_VERSION

    def to_dict(self) -> dict[str, Any]:
        d = self._payload_determinista()
        d["metadata_corrida"] = self.metadata_corrida.to_dict() if self.metadata_corrida else None
        return d

    def to_dict_deterministic(self) -> dict[str, Any]:
        """Igual que `to_dict()` pero sin `metadata_corrida`. Usar para snapshots."""
        return self._payload_determinista()

    def _payload_determinista(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "ruleset_version": self.ruleset_version,
            "expediente_id": self.expediente_id,
            "input_referenciado": dict(self.input_referenciado),
            "decision_global": self.decision_global,
            "resumen": dict(self.resumen),
            "reglas_evaluadas": [r.to_dict() for r in self.reglas_evaluadas],
            "hallazgos": [h.to_dict() for h in self.hallazgos],
        }
