"""
Detección de identificadores administrativos en texto de un documento.

Identificadores reconocidos:
  - SINAD       → "SINAD 250235" / "SINAD N° 250235"
  - SIAF        → "SIAF: 2603426" / "N° Exp SIAF: 2603426"
  - EXP         → "DIED2026-INT-0250235" / "OFI-2026-INT-0250235" (prefijo unidad)
  - AÑO         → "2026" desde fechas dd/mm/YYYY o YYYY-MM-DD o del propio EXP
  - PLANILLA    → "N° Planilla: 00617"
  - PEDIDO      → "N° Pedido: 572"
  - OFICIO      → "OFICIO N° 123-2026-MINEDU/DIED"

Formato canónico: `TIPO-VALOR` (valor numérico sin ceros a la izquierda,
excepto PLANILLA/PEDIDO que conservan el formato textual corto).

El módulo NO aplica pesos ni decide ganador: ese rol es del consolidador.
Aquí solo se detectan candidatos con trazabilidad (fragmento, regla).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DetectionSource:
    pagina: int | None
    fragmento: str
    regla: str


@dataclass
class DetectedCandidate:
    id_canonico: str
    tipo: str                     # sinad|siaf|exp|anio|planilla|pedido|oficio
    valor_original: str
    frecuencia: int
    fuentes: list[DetectionSource] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_canonico": self.id_canonico,
            "tipo": self.tipo,
            "valor_original": self.valor_original,
            "frecuencia": self.frecuencia,
            "fuentes": [
                {"pagina": f.pagina, "fragmento": f.fragmento, "regla": f.regla}
                for f in self.fuentes
            ],
        }


# --- Patrones tolerantes a OCR degradado y al delimitador "|" del text_reader ---
_PATRONES: list[tuple[str, str, str]] = [
    # (tipo, regex, id_regla)
    ("sinad",    r"\bSINAD\s*N?\s*[°\.ºo]?\s*[:\-]?\s*(\d{4,8})\b",                "re_sinad_v1"),
    ("siaf",     r"(?:N[°\.ºo]?\s*Exp\s*)?SIAF\s*[:\-]?\s*(\d{6,10})\b",            "re_siaf_v1"),
    ("exp",      r"\b([A-Z]{3,6})\s*(\d{4})\s*-\s*INT\s*-\s*(\d{6,8})\b",           "re_exp_prefijo_unidad"),
    ("planilla", r"N[°\.ºo]?\s*Planilla\s*[:\-]?\s*(\d{3,6})\b",                    "re_planilla_v1"),
    ("pedido",   r"N[°\.ºo]?\s*Pedido\s*[:\-]?\s*(\d{3,6})\b",                      "re_pedido_v1"),
    ("oficio",   r"\bOFICIO\s+N?\s*[°\.ºo]?\s*(\d{1,5}-\d{4}-[A-Z/\-]+)\b",         "re_oficio_v1"),
]

# AÑO: se extrae de fechas dd/mm/YYYY, YYYY-MM-DD, o del EXP
_RE_FECHA_SLASH = re.compile(r"\b\d{1,2}/\d{1,2}/(\d{4})\b")
_RE_FECHA_ISO = re.compile(r"\b(\d{4})-\d{2}-\d{2}\b")

# Marcador del text_reader: ===== PAGE N (motor=...) =====
_RE_PAGE_MARKER = re.compile(r"=====\s*PAGE\s+(\d+)\s*\([^)]*\)\s*=====")


def _num_sin_ceros_izq(s: str) -> str:
    s = s.lstrip("0")
    return s or "0"


def _construir_id_canonico(tipo: str, groups: tuple[str, ...]) -> tuple[str, str]:
    """
    Devuelve (id_canonico, valor_original_limpio).
    """
    if tipo == "sinad":
        v = _num_sin_ceros_izq(groups[0])
        return f"SINAD-{v}", groups[0]
    if tipo == "siaf":
        v = _num_sin_ceros_izq(groups[0])
        return f"SIAF-{v}", groups[0]
    if tipo == "exp":
        unidad = groups[0].upper()
        anio = groups[1]
        correlativo = _num_sin_ceros_izq(groups[2])
        valor_orig = f"{unidad}{anio}-INT-{groups[2]}"
        return f"EXP-{unidad}-{anio}-{correlativo}", valor_orig
    if tipo == "planilla":
        return f"PLANILLA-{groups[0]}", groups[0]
    if tipo == "pedido":
        return f"PEDIDO-{groups[0]}", groups[0]
    if tipo == "oficio":
        return f"OFICIO-{groups[0]}", groups[0]
    return f"{tipo.upper()}-{groups[0]}", groups[0]


def _mapear_pagina(texto: str, pos: int) -> int | None:
    """Mapea una posición del texto a número de página leyendo el último marcador."""
    encabezado = texto[:pos]
    matches = list(_RE_PAGE_MARKER.finditer(encabezado))
    if not matches:
        return None
    try:
        return int(matches[-1].group(1))
    except ValueError:
        return None


def _fragmento_entorno(texto: str, start: int, end: int, radio: int = 60) -> str:
    frag = texto[max(0, start - radio) : end + radio]
    frag = re.sub(r"\s+", " ", frag).strip()
    return frag[:200]


def _extraer_anio_del_texto(texto: str) -> tuple[str | None, list[DetectionSource]]:
    """Año más frecuente de fechas dd/mm/YYYY o YYYY-MM-DD en todo el texto."""
    conteo: dict[str, int] = defaultdict(int)
    fuentes: list[DetectionSource] = []
    for m in _RE_FECHA_SLASH.finditer(texto):
        y = m.group(1)
        conteo[y] += 1
        if len(fuentes) < 3:
            fuentes.append(
                DetectionSource(
                    pagina=_mapear_pagina(texto, m.start()),
                    fragmento=_fragmento_entorno(texto, m.start(), m.end()),
                    regla="re_fecha_slash",
                )
            )
    for m in _RE_FECHA_ISO.finditer(texto):
        y = m.group(1)
        conteo[y] += 1
        if len(fuentes) < 3:
            fuentes.append(
                DetectionSource(
                    pagina=_mapear_pagina(texto, m.start()),
                    fragmento=_fragmento_entorno(texto, m.start(), m.end()),
                    regla="re_fecha_iso",
                )
            )
    if not conteo:
        return None, []
    # año ganador: el más frecuente; empates → el más reciente
    anios_ordenados = sorted(conteo.items(), key=lambda kv: (-kv[1], -int(kv[0])))
    return anios_ordenados[0][0], fuentes


def detectar_candidatos(texto: str, nombre_archivo: str = "") -> list[DetectedCandidate]:
    """
    Detecta todos los candidatos en un documento. Devuelve lista ordenada por
    frecuencia desc. No aplica pesos ni decide ganador.
    """
    texto = texto or ""
    agg: dict[tuple[str, str], DetectedCandidate] = {}

    for tipo, patron, regla in _PATRONES:
        try:
            rx = re.compile(patron, re.IGNORECASE)
        except re.error:
            continue
        for m in rx.finditer(texto):
            grupos = m.groups()
            try:
                id_canonico, valor_orig = _construir_id_canonico(tipo, grupos)
            except Exception:
                continue
            clave = (tipo, id_canonico)
            if clave not in agg:
                agg[clave] = DetectedCandidate(
                    id_canonico=id_canonico,
                    tipo=tipo,
                    valor_original=valor_orig,
                    frecuencia=0,
                    fuentes=[],
                )
            cand = agg[clave]
            cand.frecuencia += 1
            if len(cand.fuentes) < 5:
                cand.fuentes.append(
                    DetectionSource(
                        pagina=_mapear_pagina(texto, m.start()),
                        fragmento=_fragmento_entorno(texto, m.start(), m.end()),
                        regla=regla,
                    )
                )
            # Si tipo=exp, también emitir un ANIO candidato desde el año del EXP
            if tipo == "exp" and len(grupos) >= 2 and grupos[1].isdigit():
                anio_exp = grupos[1]
                clave_anio = ("anio", f"ANIO-{anio_exp}")
                if clave_anio not in agg:
                    agg[clave_anio] = DetectedCandidate(
                        id_canonico=f"ANIO-{anio_exp}",
                        tipo="anio",
                        valor_original=anio_exp,
                        frecuencia=0,
                        fuentes=[],
                    )
                agg[clave_anio].frecuencia += 1
                if len(agg[clave_anio].fuentes) < 3:
                    agg[clave_anio].fuentes.append(
                        DetectionSource(
                            pagina=_mapear_pagina(texto, m.start()),
                            fragmento=_fragmento_entorno(texto, m.start(), m.end()),
                            regla="anio_desde_exp",
                        )
                    )

    # AÑO desde fechas del texto
    anio_fechas, fuentes_anio = _extraer_anio_del_texto(texto)
    if anio_fechas:
        clave_anio = ("anio", f"ANIO-{anio_fechas}")
        if clave_anio not in agg:
            agg[clave_anio] = DetectedCandidate(
                id_canonico=f"ANIO-{anio_fechas}",
                tipo="anio",
                valor_original=anio_fechas,
                frecuencia=0,
                fuentes=[],
            )
        cand = agg[clave_anio]
        cand.frecuencia += sum(1 for _ in fuentes_anio)  # conservador: sumamos las vistas
        for f in fuentes_anio:
            if len(cand.fuentes) < 5:
                cand.fuentes.append(f)

    # Candidato extra desde el nombre del archivo (peso bajo; solo referencia)
    _detectar_en_nombre(nombre_archivo, agg)

    out = list(agg.values())
    out.sort(key=lambda c: (-c.frecuencia, c.tipo, c.id_canonico))
    return out


def _detectar_en_nombre(nombre: str, agg: dict[tuple[str, str], DetectedCandidate]) -> None:
    if not nombre:
        return
    for tipo, patron, regla in _PATRONES:
        try:
            rx = re.compile(patron, re.IGNORECASE)
        except re.error:
            continue
        for m in rx.finditer(nombre):
            grupos = m.groups()
            try:
                id_canonico, valor_orig = _construir_id_canonico(tipo, grupos)
            except Exception:
                continue
            clave = (tipo, id_canonico)
            if clave not in agg:
                agg[clave] = DetectedCandidate(
                    id_canonico=id_canonico,
                    tipo=tipo,
                    valor_original=valor_orig,
                    frecuencia=0,
                    fuentes=[],
                )
            cand = agg[clave]
            # No contamos la frecuencia del nombre para no inflar;
            # solo dejamos una fuente diagnóstica.
            if not any(f.regla == f"{regla}_nombre_archivo" for f in cand.fuentes):
                cand.fuentes.append(
                    DetectionSource(
                        pagina=None,
                        fragmento=f"nombre_archivo:{nombre}",
                        regla=f"{regla}_nombre_archivo",
                    )
                )
