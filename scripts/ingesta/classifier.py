"""
Clasificador documental por reglas regex.

Categorías del prompt de negocio:
  solicitud | oficio | anexo | factura | orden_servicio |
  orden_compra | pasaje | rendicion | otros | tipo_desconocido

Estrategia:
  - Cada regla aporta un puntaje si hay match en el texto o nombre del archivo.
  - Tipo detectado = categoría con mayor puntaje total.
  - Confianza = top_score / (top_score + segundo_score + 1) ∈ (0, 1].
  - Si top_score < UMBRAL_MINIMO → "tipo_desconocido".

El texto entra tal como lo devolvió el text_reader (puede contener marcas
`===== PAGE N =====`). Las reglas son case-insensitive.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


CATEGORIAS = (
    "solicitud",
    "oficio",
    "anexo",
    "factura",
    "orden_servicio",
    "orden_compra",
    "pasaje",
    "rendicion",
    "otros",
)

_UMBRAL_MINIMO = 3


@dataclass
class ReglaMatch:
    categoria: str
    regla: str
    peso: int
    fragmento: str


@dataclass
class ClassificationResult:
    tipo_detectado: str
    confianza: float
    puntajes: dict[str, int]
    reglas_activadas: list[ReglaMatch] = field(default_factory=list)
    subtipos_detectados: list[str] = field(default_factory=list)
    nota: str = ""


# (categoria, patron, peso, id_regla, ambito)  ambito ∈ {"texto", "encabezado", "nombre"}
#   encabezado = primeras ~2000 chars (útil para meta-tipo de PDFs consolidados
#   que pegan facturas como sustento de rendición; peso x2 por alcance).
_REGLAS: list[tuple[str, str, int, str, str]] = [
    # --- rendicion ---
    ("rendicion", r"RENDICI[ÓO]N\s+DE\s+CUENTAS", 6, "rendicion_titulo", "texto"),
    ("rendicion", r"ANEXO\s*N[º°]?\s*3", 5, "anexo3_cabecera", "encabezado"),
    ("rendicion", r"M[óo]dulo\s+de\s+Tesorer", 4, "siga_tesoreria_cabecera", "encabezado"),
    ("rendicion", r"DECLARACI[ÓO]N\s+JURADA\s+DE\s+GASTOS", 3, "declaracion_jurada_gastos", "texto"),
    ("rendicion", r"RENDIC", 3, "rendicion_nombre", "nombre"),

    # --- solicitud (viáticos/comisión: planilla y solicitud formal son ambas autorizaciones previas) ---
    ("solicitud", r"SOLICITUD\s+DE\s+VI[ÁA]TIC", 6, "solicitud_viaticos", "texto"),
    ("solicitud", r"PLANILLA\s+DE\s+VI[ÁA]TIC", 6, "planilla_viaticos_cabecera", "encabezado"),
    ("solicitud", r"\bSOLICITA\b[^.\n]{0,200}\b(AUTORIZ|VI[ÁA]TIC|COMISI)", 3, "verbo_solicita_ctx", "texto"),
    ("solicitud", r"^\s*PV\d|[_\-]PV\d", 2, "prefijo_PV_nombre", "nombre"),
    ("solicitud", r"[_\-]SOL[_\-]|^\s*SOL", 2, "prefijo_SOL_nombre", "nombre"),

    # --- oficio ---
    ("oficio", r"OFICIO\s+M[ÚU]LTIPLE\s+N", 5, "oficio_multiple", "texto"),
    ("oficio", r"\bOFICIO\s+N[º°]\s*\d", 5, "oficio_con_numero", "texto"),
    ("oficio", r"\bOF\.?\s*N[º°]\s*\d", 3, "oficio_abreviado", "texto"),

    # --- factura ---
    ("factura", r"FACTURA\s+ELECTR[ÓO]NICA", 5, "factura_electronica", "texto"),
    ("factura", r"REPRESENTACI[ÓO]N\s+IMPRESA\s+DE\s+LA\s+FACTURA", 4, "factura_repr_impresa", "texto"),
    ("factura", r"BOLETA\s+DE\s+VENTA\s+ELECTR[ÓO]NICA", 4, "boleta_electronica", "texto"),
    ("factura", r"\b[EF]\d{3}-\d{2,8}\b", 2, "serie_FE_tipo", "texto"),
    ("factura", r"R\.?U\.?C\.?\s*:?\s*\d{11}.{0,400}IGV", 2, "ruc_con_igv", "texto"),

    # --- orden_servicio / orden_compra ---
    ("orden_servicio", r"ORDEN\s+DE\s+SERVICIO", 6, "orden_servicio_titulo", "texto"),
    ("orden_servicio", r"\bOS[\s\-]N[º°]?\s*\d", 3, "os_abrev", "texto"),
    ("orden_compra", r"ORDEN\s+DE\s+COMPRA", 6, "orden_compra_titulo", "texto"),
    ("orden_compra", r"\bOC[\s\-]N[º°]?\s*\d", 3, "oc_abrev", "texto"),

    # --- pasaje ---
    ("pasaje", r"TARJETA\s+DE\s+EMBARQUE|BOARDING\s+PASS", 6, "boarding_pass", "texto"),
    ("pasaje", r"PASAJE\s+A[ÉE]REO|\bVUELO\s+N[º°]?\s*\w", 4, "pasaje_aereo", "texto"),
    ("pasaje", r"\b(LATAM|SKY\s+AIRLINE|VIVA\s+AIR|JETSMART|STAR\s+PER|AVIANCA)\b", 3, "aerolinea", "texto"),

    # --- anexo (solo si no es rendicion/informe principal) ---
    ("anexo", r"^\s*ANEXO\s+N[º°]?\s*\d", 3, "anexo_titulo_encabezado", "texto"),

    # --- otros (documentos tipicos MINEDU que no cuadran en las anteriores) ---
    ("otros", r"INFORME\s+DE\s+COMISI[ÓO]N", 4, "informe_comision", "texto"),
    ("otros", r"NOTA\s+DE\s+PAGO", 4, "nota_pago", "texto"),
    ("otros", r"RECIBO\s+DE\s+INGRESO|DEVOLUCI[ÓO]N\s+DE\s+VI[ÁA]TIC", 4, "recibo_ingreso_devol", "texto"),
]


_ENCABEZADO_CHARS = 2000


def _contar_activaciones(
    regex: re.Pattern, ambito: str, texto: str, nombre: str, encabezado: str
) -> tuple[int, str]:
    """Devuelve (n_matches, fragmento_primer_match_recortado)."""
    if ambito == "nombre":
        target = nombre
    elif ambito == "encabezado":
        target = encabezado
    else:
        target = texto
    if not target:
        return 0, ""
    matches = list(regex.finditer(target))
    if not matches:
        return 0, ""
    frag = matches[0].group(0)
    return len(matches), frag[:140]


def _extract_encabezado(texto: str) -> str:
    """Primeras N chars saltando el marcador `===== PAGE 1 ... =====` del text_reader."""
    if not texto:
        return ""
    m = re.search(r"=====\s*PAGE\s+1\b.*?=====\s*", texto)
    start = m.end() if m else 0
    return texto[start : start + _ENCABEZADO_CHARS]


def classify(texto: str, nombre_archivo: str = "") -> ClassificationResult:
    """Clasifica un documento por reglas regex. Idempotente y determinista."""
    puntajes: dict[str, int] = {c: 0 for c in CATEGORIAS}
    activadas: list[ReglaMatch] = []
    encabezado = _extract_encabezado(texto)

    for categoria, patron, peso, regla_id, ambito in _REGLAS:
        try:
            rx = re.compile(patron, re.IGNORECASE | re.MULTILINE)
        except re.error:
            continue
        n, frag = _contar_activaciones(rx, ambito, texto, nombre_archivo, encabezado)
        if n > 0:
            # Limitar contribución por regla. Encabezado y nombre pesan una sola vez;
            # texto completo cap a 3 repeticiones.
            if ambito == "texto":
                contribucion = peso * min(n, 3)
            else:
                contribucion = peso
            puntajes[categoria] += contribucion
            activadas.append(ReglaMatch(categoria, regla_id, contribucion, frag))

    orden = sorted(puntajes.items(), key=lambda kv: kv[1], reverse=True)
    top, top_score = orden[0]
    segundo_score = orden[1][1] if len(orden) > 1 else 0

    if top_score < _UMBRAL_MINIMO:
        return ClassificationResult(
            tipo_detectado="tipo_desconocido",
            confianza=0.0,
            puntajes=puntajes,
            reglas_activadas=activadas,
        )

    subtipos = [c for c, p in orden[1:] if p >= _UMBRAL_MINIMO]
    nota = ""

    # Override consolidado: PDFs de rendición MINEDU pegan facturas/pasajes como sustento.
    # Si el nombre indica rendición y hay señal de rendición presente, el tipo final es
    # `rendicion` aunque las facturas anidadas acumulen más puntaje. Marca trazable.
    nombre_rendicion = bool(re.search(r"RENDIC|RENDICI[ÓO]N", nombre_archivo, re.I))
    if (
        nombre_rendicion
        and puntajes["rendicion"] >= _UMBRAL_MINIMO
        and top != "rendicion"
    ):
        nota = (
            f"override_consolidado_rendicion: top_regex={top}({top_score}) "
            f"pero filename+encabezado indican rendicion({puntajes['rendicion']})"
        )
        subtipos = [top] + [c for c in subtipos if c != "rendicion"]
        top = "rendicion"
        top_score = puntajes["rendicion"]

    confianza = round(top_score / (top_score + segundo_score + 1.0), 3)
    return ClassificationResult(
        tipo_detectado=top,
        confianza=confianza,
        puntajes=puntajes,
        reglas_activadas=[r for r in activadas if r.categoria == top],
        subtipos_detectados=subtipos,
        nota=nota,
    )
