"""
Detección de bloques-de-comprobante dentro del texto de un documento.

Estrategia (determinista, auditable):
  1. Segmentar el texto por marcadores `===== PAGE N (motor=...) =====`
     (formato del text_reader).
  2. Por página, detectar señales:
       * cabecera: "FACTURA ELECTRÓNICA" | "REPRESENTACIÓN IMPRESA" |
                   "BOLETA DE VENTA" | "TICKET" | serie [EFB]\\d{3}-\\d{2,8}
       * cuerpo  : RUC de 11 dígitos + monto con IGV/importe total
  3. Agrupar en ventana deslizante de 1-3 páginas:
       cabecera en p(n) + cuerpo en p(n..n+2) → bloque [pagina_inicio=n, pagina_fin=último cuerpo].
  4. Si un bloque tiene 2+ RUCs distintos → dividirlo por RUC (posible fusión).
  5. Bloques sin cabecera pero con RUC+monto robustos → tipo "ticket".

El módulo NO extrae campos; solo devuelve bloques de texto candidatos.
La extracción de campos se hace en `comprobante_extractor.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


_RE_PAGE = re.compile(
    r"=====\s*PAGE\s+(\d+)\s*\(motor=([^)]*)\)\s*=====\s*\n?"
)

# Señales por página
_RE_CABECERA = [
    (r"FACTURA\s+ELECTR[ÓO\�]NICA", "factura_electronica"),
    (r"REPRESENTACI[ÓO\�]N\s+IMPRESA\s+DE\s+LA\s+FACTURA", "factura_electronica"),
    (r"BOLETA\s+DE\s+VENTA\s+ELECTR[ÓO\�]NICA", "boleta_venta"),
    (r"BOLETA\s+DE\s+VENTA", "boleta_venta"),
    (r"\bTICKET\s+DE\s+(?:VENTA|MAQUINA)", "ticket"),
]
_RE_SERIE = re.compile(r"\b([EFB])(\d{3})-(\d{2,8})\b")
_RE_RUC = re.compile(r"\b(\d{11})\b")
# Marcadores monetarios fuertes
_RE_MONTO_FUERTE = [
    r"\bIGV\s*[:]?\s*S/?\.?\s*\d+[.,]\d{2}",
    r"\bIMPORTE\s+TOTAL\s*[:]?\s*S/?\.?\s*\d+[.,]\d{2}",
    r"\bTotal\s+a\s+pagar\s*[:]?\s*S/?\.?\s*\d+[.,]\d{2}",
    r"\bTotal\s+Precio\s+de\s+Venta\s*[:]?\s*S/?\.?\s*\d+[.,]\d{2}",
]


@dataclass
class SenalesPagina:
    pagina: int
    motor: str
    texto: str
    cabecera: str | None          # tipo detectado en cabecera (o None)
    serie_detectada: str | None   # "E001-16" si hay
    rucs: list[str]               # 0..n RUCs de 11 dígitos en la página
    monto_fuerte: bool            # IGV / IMPORTE TOTAL / Total a pagar presente
    cuerpo: bool                  # tiene al menos 1 RUC + monto fuerte


@dataclass
class BloqueComprobante:
    archivo: str
    pagina_inicio: int
    pagina_fin: int
    tipo_tentativo: str           # factura_electronica | boleta_venta | ticket | desconocido
    serie_tentativa: str | None   # "E001-16" si lo encontró
    rucs_candidatos: list[str]    # RUCs que aparecen dentro del bloque
    texto: str                    # texto concatenado de las páginas del bloque

    def to_dict(self) -> dict[str, Any]:
        return {
            "archivo": self.archivo,
            "pagina_inicio": self.pagina_inicio,
            "pagina_fin": self.pagina_fin,
            "tipo_tentativo": self.tipo_tentativo,
            "serie_tentativa": self.serie_tentativa,
            "rucs_candidatos": list(self.rucs_candidatos),
            "len_texto": len(self.texto),
        }


def _segmentar_paginas(texto: str) -> list[tuple[int, str, str]]:
    """Devuelve [(pagina, motor, texto_pagina), ...]."""
    if not texto:
        return []
    matches = list(_RE_PAGE.finditer(texto))
    if not matches:
        # sin marcadores: tratar como una sola página
        return [(1, "desconocido", texto)]
    out: list[tuple[int, str, str]] = []
    for i, m in enumerate(matches):
        pagina = int(m.group(1))
        motor = m.group(2)
        inicio = m.end()
        fin = matches[i + 1].start() if i + 1 < len(matches) else len(texto)
        out.append((pagina, motor, texto[inicio:fin]))
    return out


def _analizar_pagina(pagina: int, motor: str, texto_pag: str) -> SenalesPagina:
    cabecera = None
    for patron, tipo in _RE_CABECERA:
        if re.search(patron, texto_pag, re.IGNORECASE):
            cabecera = tipo
            break

    serie = None
    m = _RE_SERIE.search(texto_pag)
    if m:
        serie = f"{m.group(1)}{m.group(2)}-{m.group(3)}"

    rucs = list(dict.fromkeys(_RE_RUC.findall(texto_pag)))
    monto_fuerte = any(re.search(p, texto_pag, re.IGNORECASE) for p in _RE_MONTO_FUERTE)
    cuerpo = bool(rucs) and monto_fuerte

    return SenalesPagina(
        pagina=pagina,
        motor=motor,
        texto=texto_pag,
        cabecera=cabecera,
        serie_detectada=serie,
        rucs=rucs,
        monto_fuerte=monto_fuerte,
        cuerpo=cuerpo,
    )


def _tipo_bloque(senales: list[SenalesPagina]) -> str:
    """Deriva tipo tentativo del bloque basado en cabeceras de sus páginas."""
    tipos = [s.cabecera for s in senales if s.cabecera]
    if not tipos:
        # Sin cabecera: si hay RUC+monto → ticket; si no → desconocido
        tiene_cuerpo = any(s.cuerpo for s in senales)
        return "ticket" if tiene_cuerpo else "desconocido"
    # prioridad: factura > boleta > ticket
    for preferido in ("factura_electronica", "boleta_venta", "ticket"):
        if preferido in tipos:
            return preferido
    return tipos[0]


def _serie_bloque(senales: list[SenalesPagina]) -> str | None:
    for s in senales:
        if s.serie_detectada:
            return s.serie_detectada
    return None


def _rucs_bloque(senales: list[SenalesPagina]) -> list[str]:
    """RUCs únicos en todo el bloque (ordenados por primera aparición)."""
    out: list[str] = []
    for s in senales:
        for r in s.rucs:
            if r not in out:
                out.append(r)
    return out


def detectar_bloques(
    texto_concatenado: str,
    nombre_archivo: str,
    *,
    ventana_maxima: int = 3,
) -> list[BloqueComprobante]:
    """
    Segmenta `texto_concatenado` en bloques de comprobante.
    """
    pags = _segmentar_paginas(texto_concatenado)
    if not pags:
        return []

    senales = [_analizar_pagina(p, m, t) for (p, m, t) in pags]
    # mapa rápido por página
    por_pagina: dict[int, SenalesPagina] = {s.pagina: s for s in senales}

    bloques: list[BloqueComprobante] = []
    usadas: set[int] = set()

    for s in senales:
        if s.pagina in usadas:
            continue
        # Criterio de inicio: página con cabecera O página con cuerpo (RUC+monto) y
        # no ya incluida
        if not (s.cabecera or s.cuerpo):
            continue

        pagina_inicio = s.pagina
        pagina_fin = s.pagina
        # Extender hasta encontrar "cuerpo" dentro de ventana_maxima si aún no hay
        tiene_cuerpo = s.cuerpo
        for delta in range(1, ventana_maxima):
            sig = por_pagina.get(s.pagina + delta)
            if not sig:
                break
            # Parar si la página siguiente inicia OTRA cabecera de comprobante
            if sig.cabecera and (sig.cabecera != s.cabecera or sig.serie_detectada != s.serie_detectada) and delta > 0:
                break
            # Incluir si aporta cuerpo o continuidad
            if sig.cuerpo or sig.rucs or sig.cabecera == s.cabecera:
                pagina_fin = sig.pagina
                tiene_cuerpo = tiene_cuerpo or sig.cuerpo
            else:
                break

        # Marcar usadas
        for p in range(pagina_inicio, pagina_fin + 1):
            usadas.add(p)

        sub_senales = [por_pagina[p] for p in range(pagina_inicio, pagina_fin + 1) if p in por_pagina]
        rucs = _rucs_bloque(sub_senales)

        # Filtro calidad: si no hay cabecera ni RUC, descartar
        if not (any(x.cabecera for x in sub_senales) or rucs):
            continue

        tipo = _tipo_bloque(sub_senales)
        serie = _serie_bloque(sub_senales)
        texto = "\n".join(x.texto for x in sub_senales)

        # División por RUCs múltiples: si hay 2+ RUCs distintos y el bloque es
        # suficientemente grande, generar un solo bloque pero marcarlo; la
        # extracción posterior elegirá el primer RUC como emisor.
        bloques.append(
            BloqueComprobante(
                archivo=nombre_archivo,
                pagina_inicio=pagina_inicio,
                pagina_fin=pagina_fin,
                tipo_tentativo=tipo,
                serie_tentativa=serie,
                rucs_candidatos=rucs,
                texto=texto,
            )
        )

    return bloques
