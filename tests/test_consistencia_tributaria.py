"""
Tests unitarios puros para `modelo.consistencia_tributaria`.

Cubren los 4 estados (OK, DIFERENCIA_LEVE, DIFERENCIA_CRITICA,
DATOS_INSUFICIENTES) y los principales tipos tributarios. Sin I/O.
"""

from __future__ import annotations

from modelo.consistencia_tributaria import evaluar_consistencia


def test_evaluar_gravada_ok():
    """Factura gravada estándar: bi + igv ≈ total con tolerancia ±1.00."""
    estado, tipo, detalle = evaluar_consistencia(
        monto_total="35.00",
        bi_gravado="29.66",
        monto_igv="5.34",
        op_exonerada=None,
        op_inafecta=None,
        recargo_consumo=None,
    )
    assert estado == "OK"
    assert tipo == "GRAVADA"
    assert "tipo=GRAVADA" in detalle


def test_evaluar_diferencia_leve():
    """Suma de componentes difiere del total entre 1.00 y 5.00 → LEVE.

    bi + igv = 35.00; total = 37.00; delta = +2.00.
    """
    estado, tipo, _detalle = evaluar_consistencia(
        monto_total="37.00",
        bi_gravado="29.66",
        monto_igv="5.34",
        op_exonerada=None,
        op_inafecta=None,
        recargo_consumo=None,
    )
    assert estado == "DIFERENCIA_LEVE"
    assert tipo == "GRAVADA"


def test_evaluar_diferencia_critica():
    """Suma de componentes difiere del total más de 5.00 → CRITICA.

    bi + igv = 35.00; total = 85.00; delta = +50.00.
    """
    estado, tipo, _detalle = evaluar_consistencia(
        monto_total="85.00",
        bi_gravado="29.66",
        monto_igv="5.34",
        op_exonerada=None,
        op_inafecta=None,
        recargo_consumo=None,
    )
    assert estado == "DIFERENCIA_CRITICA"
    assert tipo == "GRAVADA"


def test_evaluar_datos_insuficientes_total_none():
    """Falta monto_total: no se puede validar nada; tipo no se clasifica."""
    estado, tipo, detalle = evaluar_consistencia(
        monto_total=None,
        bi_gravado="29.66",
        monto_igv="5.34",
        op_exonerada=None,
        op_inafecta=None,
        recargo_consumo=None,
    )
    assert estado == "DATOS_INSUFICIENTES"
    assert tipo == ""
    assert detalle == "falta monto_total"


def test_evaluar_datos_insuficientes_componentes_cero():
    """Total > 0 pero todos los componentes son 0: desglose no capturado."""
    estado, tipo, detalle = evaluar_consistencia(
        monto_total="80.00",
        bi_gravado="0.00",
        monto_igv="0.00",
        op_exonerada="0.00",
        op_inafecta="0.00",
        recargo_consumo="0.00",
    )
    assert estado == "DATOS_INSUFICIENTES"
    assert tipo == ""
    assert "desglose tributario no capturado" in detalle


def test_evaluar_exonerada_rule2():
    """Rule 2: op_exonerada > 0 con IGV = 0 → total = op_exonerada → OK EXONERADA."""
    estado, tipo, detalle = evaluar_consistencia(
        monto_total="80.00",
        bi_gravado=None,
        monto_igv="0.00",
        op_exonerada="80.00",
        op_inafecta=None,
        recargo_consumo=None,
    )
    assert estado == "OK"
    assert tipo == "EXONERADA"
    assert "tipo=EXONERADA" in detalle
