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

from ingesta.classifier import classify_page


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
    # Clasificación tripartita (F1): comprobante_real | soporte_sunat | administrativo | otros
    categoria_pagina: str = "otros"
    subtipo_pagina: str = ""


@dataclass
class BloqueComprobante:
    archivo: str
    pagina_inicio: int
    pagina_fin: int
    tipo_tentativo: str           # factura_electronica | boleta_venta | ticket | desconocido
    serie_tentativa: str | None   # "E001-16" si lo encontró
    rucs_candidatos: list[str]    # RUCs que aparecen dentro del bloque
    texto: str                    # texto concatenado de las páginas del bloque
    razon_social_tentativa: str | None = None  # desde página consulta RUC (texto seleccionable)

    def to_dict(self) -> dict[str, Any]:
        return {
            "archivo": self.archivo,
            "pagina_inicio": self.pagina_inicio,
            "pagina_fin": self.pagina_fin,
            "tipo_tentativo": self.tipo_tentativo,
            "serie_tentativa": self.serie_tentativa,
            "rucs_candidatos": list(self.rucs_candidatos),
            "razon_social_tentativa": self.razon_social_tentativa,
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

    # F1: clasificación tripartita por página. Gana sobre las heurísticas
    # locales; si la página es SUNAT o administrativa NUNCA abrirá un bloque.
    pc = classify_page(texto_pag)

    return SenalesPagina(
        pagina=pagina,
        motor=motor,
        texto=texto_pag,
        cabecera=cabecera,
        serie_detectada=serie,
        rucs=rucs,
        monto_fuerte=monto_fuerte,
        cuerpo=cuerpo,
        categoria_pagina=pc.categoria_pagina,
        subtipo_pagina=pc.subtipo,
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
        # Nuevo criterio de inicio (F2): SOLO páginas clasificadas como
        # `comprobante_real` pueden abrir un bloque. Las páginas SUNAT y
        # administrativas se excluyen aquí (antes se colaban como "ticket"
        # por tener RUC + monto).
        if s.categoria_pagina != "comprobante_real":
            continue

        pagina_inicio = s.pagina
        pagina_fin = s.pagina
        tiene_cuerpo = s.cuerpo
        for delta in range(1, ventana_maxima):
            sig = por_pagina.get(s.pagina + delta)
            if not sig:
                break
            # Cerrar si la página siguiente es SUNAT o administrativa — esas
            # nunca extienden el comprobante (irán a sus propias hojas).
            if sig.categoria_pagina in ("soporte_sunat", "administrativo"):
                break
            # Cerrar si la página siguiente inicia OTRO comprobante distinto.
            if sig.cabecera and (sig.cabecera != s.cabecera or sig.serie_detectada != s.serie_detectada):
                break
            # Solo extender dentro de páginas comprobante_real que aporten
            # cuerpo, RUC o continuidad de cabecera.
            if sig.categoria_pagina == "comprobante_real" and (
                sig.cuerpo or sig.rucs or sig.cabecera == s.cabecera
            ):
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

    # -----------------------------------------------------------------
    # Segundo pase: recuperar comprobantes escaneados vía CPE.
    #
    # Las páginas CPE (sunat_validez_cpe) citan la cabecera del
    # comprobante consultado.  Si la página inmediata anterior está
    # clasificada como "otros" y no fue usada, es un comprobante real
    # cuyo OCR no capturó la cabecera.  Tipo y serie se extraen del
    # texto CPE (más fiable que el escaneo); RUC de la página de
    # consulta RUC que sigue a la CPE.
    # -----------------------------------------------------------------
    for s in senales:
        if s.subtipo_pagina != "sunat_validez_cpe":
            continue
        cand = por_pagina.get(s.pagina - 1)
        if not cand or cand.categoria_pagina != "otros" or cand.pagina in usadas:
            continue

        tipo_cpe = "desconocido"
        for patron, tipo_label in _RE_CABECERA:
            if re.search(patron, s.texto, re.IGNORECASE):
                tipo_cpe = tipo_label
                break

        serie_cpe = None
        m_serie = _RE_SERIE.search(s.texto)
        if m_serie:
            serie_cpe = f"{m_serie.group(1)}{m_serie.group(2)}-{m_serie.group(3)}"

        rucs_cpe: list[str] = []
        ruc_pag = por_pagina.get(s.pagina + 1)
        if ruc_pag and ruc_pag.subtipo_pagina == "sunat_ruc":
            rucs_cpe = list(dict.fromkeys(_RE_RUC.findall(ruc_pag.texto)))
        if not rucs_cpe:
            rucs_cpe = list(dict.fromkeys(_RE_RUC.findall(cand.texto)))

        usadas.add(cand.pagina)
        bloques.append(
            BloqueComprobante(
                archivo=nombre_archivo,
                pagina_inicio=cand.pagina,
                pagina_fin=cand.pagina,
                tipo_tentativo=tipo_cpe,
                serie_tentativa=serie_cpe,
                rucs_candidatos=rucs_cpe,
                texto=cand.texto,
            )
        )

    bloques.sort(key=lambda b: b.pagina_inicio)

    # -----------------------------------------------------------------
    # Enriquecimiento: razón social + serie desde páginas CPE/RUC.
    #
    # Para cada bloque, buscar por posición la primera sunat_validez_cpe
    # después de pagina_fin. Desde ahí:
    #   - Serie: extraer del texto CPE (formato amplio: FA01-NNN, EB01-NNN,
    #     FF01-NNN, etc.; el regex local acepta letras intermedias y
    #     correlativos de hasta 10 dígitos, más amplio que _RE_SERIE).
    #   - Razón social: extraer de la primera sunat_ruc después de la CPE.
    # -----------------------------------------------------------------
    _re_razon = re.compile(
        r"N[uú\ufffd]mero\s+de\s+RUC\s*:\s*\n?\s*(\d{11})\s*-\s*(.+)", re.IGNORECASE
    )
    _re_serie_cpe = re.compile(r"\b([EFB][A-Z]?\d{2,3})-(\d{1,10})\b")

    for bloque in bloques:
        necesita_razon = not bloque.razon_social_tentativa
        necesita_serie = not bloque.serie_tentativa
        if not necesita_razon and not necesita_serie:
            continue
        pag_cpe = None
        for delta in range(1, 4):
            sp = por_pagina.get(bloque.pagina_fin + delta)
            if sp and sp.subtipo_pagina == "sunat_validez_cpe":
                pag_cpe = sp
                break
        if pag_cpe is None:
            continue
        if necesita_serie:
            m_serie = _re_serie_cpe.search(pag_cpe.texto)
            if m_serie:
                bloque.serie_tentativa = f"{m_serie.group(1)}-{m_serie.group(2)}"
        if necesita_razon:
            for delta in range(1, 3):
                sp = por_pagina.get(pag_cpe.pagina + delta)
                if sp and sp.subtipo_pagina == "sunat_ruc":
                    m_razon = _re_razon.search(sp.texto)
                    if m_razon:
                        bloque.razon_social_tentativa = m_razon.group(2).strip()
                    break

    return bloques
