"""
Consistencia tributaria de comprobantes — funciones puras y deterministas.

Validan que `monto_total` cuadre con la suma de los componentes tributarios
(`bi_gravado`, `monto_igv`, `op_exonerada`, `op_inafecta`, `recargo_consumo`)
según la jerarquía conceptual del comprobante (GRAVADA / EXONERADA /
INAFECTA / MIXTA / NO_DETERMINABLE).

Origen: lógica trasladada desde `scripts/ingest_expedientes.py` (D-19,
2026-04-21) para que el cálculo viva en la capa de modelo y pueda
persistirse en `expediente.json` (schema `expediente.v4`) en lugar de
recalcularse al exportar Excel. Ver D-24 (PRE-PASO 4.5).

Contrato:
  evaluar_consistencia(...) -> (estado, tipo_tributario, detalle)
    estado          ∈ {OK, DIFERENCIA_LEVE, DIFERENCIA_CRITICA, DATOS_INSUFICIENTES}
    tipo_tributario ∈ {GRAVADA, EXONERADA, INAFECTA, MIXTA, NO_DETERMINABLE, ""}
    detalle         : mensaje legible auditable

  Cuando estado == DATOS_INSUFICIENTES, tipo_tributario es "" porque
  no se intentó clasificar (no hay total o no hay componentes con valor).
"""

from __future__ import annotations


def clasificar_tipo_tributario(
    bi: float | None,
    igv: float | None,
    exo: float | None,
    ina: float | None,
) -> tuple[str, list[str]]:
    """Clasifica el comprobante según su naturaleza tributaria.

    Jerarquía conceptual (determinista, basada en qué componentes son > 0):
      GRAVADA       — IGV > 0  o  bi_gravado > 0 sin exo/ina
      EXONERADA     — op_exonerada > 0 sin bi gravado ni igv
      INAFECTA      — op_inafecta > 0 sin bi gravado ni igv
      MIXTA         — combina gravada con exo o ina
      NO_DETERMINABLE — todos los componentes capturados son 0 o None

    Devuelve (tipo, componentes_esperados). 'componentes_esperados' es la
    lista de campos que DEBEN sumar al total para esta clase de comprobante.
    """
    bi_pos = bi is not None and bi > 0.01
    igv_pos = igv is not None and igv > 0.01
    exo_pos = exo is not None and exo > 0.01
    ina_pos = ina is not None and ina > 0.01

    gravada_signal = igv_pos or bi_pos
    if gravada_signal and (exo_pos or ina_pos):
        return "MIXTA", ["bi_gravado", "monto_igv", "op_exonerada", "op_inafecta"]
    if gravada_signal:
        return "GRAVADA", ["bi_gravado", "monto_igv"]
    if exo_pos and not gravada_signal:
        return "EXONERADA", ["op_exonerada"]
    if ina_pos and not gravada_signal:
        return "INAFECTA", ["op_inafecta"]
    return "NO_DETERMINABLE", []


def evaluar_consistencia(
    monto_total: str | None,
    bi_gravado: str | None,
    monto_igv: str | None,
    op_exonerada: str | None,
    op_inafecta: str | None,
    recargo_consumo: str | None,
) -> tuple[str, str, str]:
    """Valida que monto_total ≈ bi + igv + exo + ina + recargo (±1.00),
    con jerarquía conceptual tributaria.

    Clasifica el comprobante en GRAVADA / EXONERADA / INAFECTA / MIXTA y
    solo marca 'faltan componentes' para los campos esperados de ese tipo.

    Reglas conceptuales aplicadas:
      - Rule 2: si op_exonerada > 0 e IGV = 0 → aceptar total = op_exonerada.
      - Rule 3: si op_inafecta > 0 e IGV = 0 → aceptar total = op_inafecta.
      - Rule 5: no pedir bi_gravado en comprobantes exonerados o inafectos.

    Estados:
      OK                   — suma de componentes del tipo cuadra ±1.00
      DIFERENCIA_LEVE      — 1.00 < |delta| ≤ 5.00
      DIFERENCIA_CRITICA   — |delta| > 5.00 o componente > total (imposible físico)
      DATOS_INSUFICIENTES  — falta total, o todos los componentes = 0/None

    Retorno: (estado, tipo_tributario, detalle).
    Cuando estado == DATOS_INSUFICIENTES, tipo_tributario es "" porque
    no se clasificó.
    """

    def _to_float(x: str | None) -> float | None:
        if x is None or x == "":
            return None
        try:
            return float(x)
        except Exception:
            return None

    total = _to_float(monto_total)
    comps = {
        "bi_gravado": _to_float(bi_gravado),
        "monto_igv": _to_float(monto_igv),
        "op_exonerada": _to_float(op_exonerada),
        "op_inafecta": _to_float(op_inafecta),
        "recargo_consumo": _to_float(recargo_consumo),
    }
    presentes = {k: v for k, v in comps.items() if v is not None}

    if total is None:
        return "DATOS_INSUFICIENTES", "", "falta monto_total"
    if not presentes:
        return (
            "DATOS_INSUFICIENTES",
            "",
            "monto_total presente pero todos los componentes vacios",
        )

    # Si todos los componentes capturados son 0 y total > 0, no hay breakdown
    # real — el desglose tributario del PDF no se capturó (OCR roto o boleta
    # simplificada sin tabla de totales). No es contradicción, es gap.
    if total > 0.01 and all((v is None or v < 0.01) for v in comps.values()):
        return (
            "DATOS_INSUFICIENTES",
            "",
            "desglose tributario no capturado (todos los componentes 0 o vacíos)",
        )

    tipo, esperados = clasificar_tipo_tributario(
        comps["bi_gravado"], comps["monto_igv"],
        comps["op_exonerada"], comps["op_inafecta"],
    )

    # Suma contable: solo considerar los componentes consistentes con el tipo.
    # - GRAVADA: bi + igv + recargo
    # - EXONERADA: op_exonerada + recargo (rule 2)
    # - INAFECTA: op_inafecta + recargo (rule 3)
    # - MIXTA: todos
    # - NO_DETERMINABLE: usar suma de todos los presentes
    if tipo == "GRAVADA":
        campos_suma = ["bi_gravado", "monto_igv", "recargo_consumo"]
    elif tipo == "EXONERADA":
        campos_suma = ["op_exonerada", "recargo_consumo"]
    elif tipo == "INAFECTA":
        campos_suma = ["op_inafecta", "recargo_consumo"]
    elif tipo == "MIXTA":
        campos_suma = ["bi_gravado", "monto_igv", "op_exonerada", "op_inafecta", "recargo_consumo"]
    else:
        campos_suma = list(comps.keys())

    suma = sum((comps[k] or 0.0) for k in campos_suma if comps.get(k) is not None)
    delta = total - suma

    # Violaciones físicas: componente > total (+1.00 holgura decimal)
    violaciones: list[str] = []
    for k, v in presentes.items():
        if v > total + 1.00:
            violaciones.append(f"posible OCR en {k} ({v:.2f} > total {total:.2f})")

    # IGV inconsistente vs bi_gravado (regla 18% Perú) — solo en GRAVADA/MIXTA
    igv_hint: str | None = None
    bi = comps.get("bi_gravado")
    igv = comps.get("monto_igv")
    if tipo in ("GRAVADA", "MIXTA") and bi is not None and igv is not None and bi > 0 and igv > 0:
        igv_esperado = bi * 0.18
        if abs(igv - igv_esperado) > 1.00:
            igv_hint = (
                f"igv inconsistente (esperado {igv_esperado:.2f} si bi {bi:.2f} "
                f"es gravada, leyó {igv:.2f})"
            )

    # Solo pedir los componentes esperados para este tipo (Rule 5).
    ausentes_relevantes = [c for c in esperados if comps.get(c) is None]

    motivos: list[str] = [f"tipo={tipo}"]
    if violaciones:
        motivos.extend(violaciones)
    if igv_hint:
        motivos.append(igv_hint)
    if ausentes_relevantes and abs(delta) > 1.00:
        motivos.append(
            f"faltan componentes esperados ({tipo}): {','.join(ausentes_relevantes)}"
        )

    if delta > 1.00:
        motivos.append(f"suma menor a total (delta={delta:+.2f})")
    elif delta < -1.00:
        motivos.append(f"suma excede total (delta={delta:+.2f})")

    abs_delta = abs(delta)
    if violaciones:
        estado = "DIFERENCIA_CRITICA"
    elif abs_delta <= 1.00:
        estado = "OK"
    elif abs_delta <= 5.00:
        estado = "DIFERENCIA_LEVE"
    else:
        estado = "DIFERENCIA_CRITICA"

    if estado == "OK" and len(motivos) == 1:
        # Solo tipo, sin anomalías — mensaje explícito de éxito.
        detalle = f"tipo={tipo}; suma={suma:.2f} vs total={total:.2f} (±1.00)"
    else:
        detalle = "; ".join(motivos)
    return estado, tipo, detalle
