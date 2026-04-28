"""
Registro ordenado de reglas MVP del PASO 4.5 + helpers compartidos.

El orden de `REGLAS` determina el orden estable en que el orquestador
las invoca y, por tanto, el orden de `reglas_evaluadas[]` en el output.
Este orden es relevante para la idempotencia byte-a-byte (regla 6).
"""

from __future__ import annotations

from typing import Callable

from modelo.decision_engine_output import (
    Hallazgo,
    ResultadoRegla,
    RESULTADO_NO_APLICABLE,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
    SEVERIDAD_ALTA,
    SEVERIDAD_BAJA,
    SEVERIDAD_MEDIA,
)


_RESULTADO_RANK = {
    RESULTADO_NO_APLICABLE: -1,
    RESULTADO_OK: 0,
    RESULTADO_OBSERVAR: 1,
    RESULTADO_REVISAR: 2,
}

_SEVERIDAD_RANK = {
    None: 0,
    SEVERIDAD_BAJA: 1,
    SEVERIDAD_MEDIA: 2,
    SEVERIDAD_ALTA: 3,
}


def peor(a: tuple[str, str | None], b: tuple[str, str | None]) -> tuple[str, str | None]:
    """De dos `(resultado, severidad)` devuelve el peor según ranking."""
    ra, sa = a
    rb, sb = b
    if _RESULTADO_RANK[ra] > _RESULTADO_RANK[rb]:
        return a
    if _RESULTADO_RANK[ra] < _RESULTADO_RANK[rb]:
        return b
    if _SEVERIDAD_RANK.get(sa, 0) >= _SEVERIDAD_RANK.get(sb, 0):
        return a
    return b


# Tipo de cada regla del MVP: función pura que dado un dict de expediente
# devuelve `(ResultadoRegla, list[Hallazgo])`. Hallazgos solo se emiten
# para resultados OBSERVAR o REVISAR (OK y NO_APLICABLE no generan).
ReglaFn = Callable[[dict], tuple[ResultadoRegla, list[Hallazgo]]]


def cargar_reglas() -> list[tuple[str, ReglaFn]]:
    """Devuelve la lista ordenada `[(regla_id, fn), ...]` del MVP.

    Importación diferida para evitar ciclos al cargar el paquete.
    """
    from auditoria.reglas import (
        r_identidad_expediente,
        r_consistencia,
        r_campo_critico_null,
        r_firmas,
        r_ue_receptor,
    )
    return [
        (r_identidad_expediente.REGLA_ID, r_identidad_expediente.evaluar),
        (r_consistencia.REGLA_ID, r_consistencia.evaluar),
        (r_campo_critico_null.REGLA_ID, r_campo_critico_null.evaluar),
        (r_firmas.REGLA_ID, r_firmas.evaluar),
        (r_ue_receptor.REGLA_ID, r_ue_receptor.evaluar),
    ]
