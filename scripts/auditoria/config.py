"""
Configuración del motor PASO 4.5 (Fase 1 MVP).

Valores tunables aislados aquí para que cada regla los importe sin
hardcoding interno. Cualquier cambio de criterio numérico debería bumpear
`RULESET_VERSION` en `scripts/modelo/decision_engine_output.py`.
"""

from __future__ import annotations


# RUC de la Unidad Ejecutora esperada como receptor de comprobantes.
#
# IMPORTANTE — VALOR TEMPORAL DE MVP:
# `20380795907` = MINEDU (única UE de los 4 expedientes piloto al 2026-04).
# Esta constante NO es universal. En fase posterior se debe derivar la UE
# esperada del propio expediente (campo de cabecera, ente emisor de la
# planilla, o configuración por proyecto/oficina). Hardcodear aquí queda
# documentado como deuda explícita del MVP.
UE_ESPERADA: str = "20380795907"


# Umbral para R-IDENTIDAD-EXPEDIENTE: por debajo de este valor de
# `resolucion_id.confianza_expediente`, la identidad se considera no
# certificable y la regla cae a REVISAR (falta de certeza, no
# incumplimiento — ajuste consensuado en diseño Fase 1).
UMBRAL_CONFIANZA_IDENTIDAD: float = 0.9
