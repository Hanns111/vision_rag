"""
Patrones regex para clasificación de páginas en 3 categorías operativas:

  * comprobante_real     — factura / boleta / ticket / recibo por honorarios
                           físico, emitido por el proveedor.
  * soporte_sunat        — consulta RUC, consulta validez CPE, padrones,
                           resultado de búsqueda. NUNCA es comprobante.
  * administrativo       — planilla viáticos, solicitud, DNI, compromiso
                           devolución, certificación presupuestaria, etc.

Las listas son constantes planas (regex, etiqueta). Ninguna lógica aquí.
La lógica de decisión vive en `classifier.classify_page()`.

Principio: un patrón está en UN solo grupo. Si uno nuevo aparece en el
piloto, se agrega aquí y se vuelve a correr `process` sin tocar código.
"""

from __future__ import annotations


# -----------------------------------------------------------------------------
# Señales SUNAT FUERTE — aparecen SOLO en páginas de consulta web SUNAT.
# Si matchean, la página NO es comprobante aunque contenga por casualidad
# cabeceras o series (las consultas CPE citan la cabecera del comprobante
# consultado como referencia). Tienen prioridad sobre cabecera.
# -----------------------------------------------------------------------------
PATRONES_SUNAT_FUERTE: list[tuple[str, str]] = [
    (r"Consulta\s+RUC", "sunat_ruc"),
    (r"Resultado\s+de\s+la\s+B[úu]squeda", "sunat_ruc"),
    (r"N[úu]mero\s+de\s+RUC\s*:", "sunat_ruc"),
    (r"Estado\s+del\s+Contribuyente", "sunat_ruc"),
    (r"Condici[óo]n\s+del\s+Contribuyente", "sunat_ruc"),
    (r"^\s*Padrones\s*:", "sunat_ruc"),
    (r"Consulta\s+(?:de\s+)?Validez\s+del\s+Comprobante\s+de\s+Pago", "sunat_validez_cpe"),
    (r"Resultado\s+de\s+la\s+Consulta", "sunat_validez_cpe"),
    (r"La\s+Factura\s+Electr[óo]nica.{0,80}comprobante\s+de\s+pago\s+v[áa]lido", "sunat_validez_cpe"),
]


# -----------------------------------------------------------------------------
# Señales SUNAT DÉBIL — leyendas/footers que aparecen tanto en comprobantes
# reales como en consultas. Nunca deciden por sí solas; solo se reportan como
# trazabilidad (senales_sunat del resultado).
# -----------------------------------------------------------------------------
PATRONES_SUNAT_DEBIL: list[tuple[str, str]] = [
    (r"Sistema\s+de\s+Emisi[óo]n\s+Electr[óo]nica", "footer_see"),
]


# Alias backwards-compat: la lista completa para casos que solo quieran
# saber si HAY cualquier señal SUNAT (fuerte o débil).
PATRONES_SOPORTE_SUNAT: list[tuple[str, str]] = (
    PATRONES_SUNAT_FUERTE + PATRONES_SUNAT_DEBIL
)


# -----------------------------------------------------------------------------
# Cabeceras de COMPROBANTE REAL — inclusión (una sola basta).
# Se usa también en comprobante_detector.py; esta es la fuente única.
# -----------------------------------------------------------------------------
PATRONES_COMPROBANTE_CABECERA: list[tuple[str, str]] = [
    (r"FACTURA\s+ELECTR[ÓO\xef\xbf\xbd]NICA", "factura_electronica"),
    (r"REPRESENTACI[ÓO\xef\xbf\xbd]N\s+IMPRESA\s+DE\s+LA\s+FACTURA", "factura_electronica"),
    (r"BOLETA\s+DE\s+VENTA\s+ELECTR[ÓO\xef\xbf\xbd]NICA", "boleta_venta"),
    (r"BOLETA\s+DE\s+VENTA", "boleta_venta"),
    (r"\bTICKET\s+DE\s+(?:VENTA|MAQUINA|M[ÁA]QUINA)", "ticket"),
    (r"RECIBO\s+POR\s+HONORARIOS", "recibo_honorarios"),
    (r"NOTA\s+DE\s+VENTA", "nota_venta"),
]


# Serie estándar de comprobantes electrónicos peruanos (F001-12345, E001-16, B001-...).
PATRON_SERIE_FE = r"\b([EFB])(\d{3})-(\d{2,8})\b"


# Señales de TOTAL positivo — confirman que la página es un comprobante real
# y no solo una consulta (las consultas rara vez muestran "Importe Total > 0").
PATRONES_TOTAL_POSITIVO: list[str] = [
    r"\bIMPORTE\s+TOTAL\s*[:]?\s*S/?\.?\s*(?!0[.,]0{1,2}\b)\d+[.,]\d{2}",
    r"\bTotal\s+a\s+pagar\s*[:]?\s*S/?\.?\s*(?!0[.,]0{1,2}\b)\d+[.,]\d{2}",
    r"\bTotal\s+Precio\s+de\s+Venta\s*[:]?\s*S/?\.?\s*(?!0[.,]0{1,2}\b)\d+[.,]\d{2}",
    r"\bMONTO\s+TOTAL\s*[:]?\s*S/?\.?\s*(?!0[.,]0{1,2}\b)\d+[.,]\d{2}",
]


# -----------------------------------------------------------------------------
# DOCUMENTOS ADMINISTRATIVOS — cualquiera basta para excluir como comprobante.
# -----------------------------------------------------------------------------
PATRONES_ADMINISTRATIVO: list[tuple[str, str]] = [
    (r"PLANILLA\s+DE\s+VI[ÁA]TIC", "planilla_viaticos"),
    (r"SOLICITUD\s+DE\s+VI[ÁA]TIC", "solicitud_viaticos"),
    (r"SOLICITUD\s+DE\s+SEGURO", "solicitud_seguro"),
    (r"PLAN\s+DE\s+TRABAJO", "plan_trabajo"),
    (r"COMPROMISO\s+DE\s+DEVOLUCI[ÓO]N", "compromiso_devolucion"),
    (r"DOCUMENTO\s+NACIONAL\s+DE\s+IDENTIDAD|\bDNI\b\s+N[º°]?\s*\d{8}", "dni"),
    (r"CERTIFICACI[ÓO]N\s+PRESUPUEST", "certificacion_presupuestaria"),
    (r"CONSTANCIA\s+DE", "constancia"),
    (r"ANEXO\s*N[º°]?\s*3\b", "anexo3"),
    (r"RENDICI[ÓO]N\s+DE\s+CUENTAS", "rendicion_cabecera"),
    (r"INFORME\s+DE\s+COMISI[ÓO]N", "informe_comision"),
    (r"DECLARACI[ÓO]N\s+JURADA\s+DE\s+GASTOS", "declaracion_jurada"),
    (r"OFICIO\s+(?:M[ÚU]LTIPLE\s+)?N[º°]?\s*\d", "oficio"),
    (r"NOTA\s+DE\s+PAGO", "nota_pago"),
    (r"RECIBO\s+DE\s+INGRESO", "recibo_ingreso"),
    (r"ALERTA\b", "alerta"),
]
