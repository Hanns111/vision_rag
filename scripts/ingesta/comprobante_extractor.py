"""
Extracción de campos por BloqueComprobante — wrapper de PASO 4.1.

Para cada bloque detectado por `comprobante_detector.detectar_bloques`,
aplica `piloto_field_extract_paso4.extract_fields_paso4` SOLO al texto
del bloque y mapea los campos al schema `Comprobante`.

Deduplicación por clave (ruc, serie_numero, fecha, monto_total). Si dos
claves están vacías, se cae a hash del texto para no fusionar tickets
distintos.

Principio: no inventa. Si el extractor devuelve None para un campo,
el `Comprobante` queda con ese campo en None y `confianza=0` para él.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

_scripts = str(Path(__file__).resolve().parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from modelo.expediente import Comprobante  # noqa: E402

# El detector importa después para evitar ciclo; se pasan los bloques ya calculados.


def _resumen_texto(s: str, n: int = 4000) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s[:n]


def _hash_bloque(archivo: str, pi: int, pf: int, texto: str) -> str:
    h = hashlib.sha1()
    h.update(f"{archivo}|{pi}|{pf}|".encode("utf-8"))
    h.update((texto[:1500] or "").encode("utf-8"))
    return h.hexdigest()[:16]


def _confianza_promedio(campos_presentes: dict[str, object]) -> float:
    """Proporción simple de campos con valor no-nulo entre los core."""
    core = ("ruc", "serie_numero", "fecha", "monto_total")
    presentes = sum(1 for k in core if campos_presentes.get(k))
    return round(presentes / len(core), 3)


def extraer_de_bloque(bloque) -> Comprobante:
    """Aplica PASO 4.1 al texto del bloque y construye un Comprobante."""
    from piloto_field_extract_paso4 import extract_fields_paso4

    fields, _trace = extract_fields_paso4(bloque.texto or "")

    # PASO 4.1 devuelve {ruc_emisor, ruc_receptor, serie_numero, razon_social_emisor,
    #                    fecha_emision, monto_subtotal, monto_igv, monto_total, moneda,
    #                    tipo_documento}
    ruc = fields.get("ruc_emisor")
    if not ruc and bloque.rucs_candidatos:
        # fallback: primer RUC del bloque
        ruc = bloque.rucs_candidatos[0]
    ruc_receptor = fields.get("ruc_receptor")

    serie = fields.get("serie_numero") or bloque.serie_tentativa
    razon = getattr(bloque, "razon_social_tentativa", None) or fields.get("razon_social_emisor")
    fecha = fields.get("fecha_emision")
    monto_total = fields.get("monto_total") or fields.get("monto_subtotal")
    moneda = fields.get("moneda")
    igv = fields.get("monto_igv")
    bi = fields.get("bi_gravado")
    exo = fields.get("op_exonerada")
    ina = fields.get("op_inafecta")
    rec = fields.get("recargo_consumo")

    presentes = {
        "ruc": ruc,
        "serie_numero": serie,
        "fecha": fecha,
        "monto_total": monto_total,
    }
    conf = _confianza_promedio(presentes)

    # Clave de deduplicación. Solo colapsar cuando hay señal ÚNICA: serie o
    # monto. RUC+fecha aislados no garantizan unicidad (un proveedor puede
    # emitir varios comprobantes el mismo día).
    claves_llenas = [v for v in (ruc, serie, fecha, monto_total) if v]
    tiene_id_fuerte = bool(serie) or bool(monto_total)
    if len(claves_llenas) >= 2 and tiene_id_fuerte:
        clave = "|".join(str(v) for v in (ruc or "", serie or "", fecha or "", monto_total or ""))
    else:
        clave = _hash_bloque(bloque.archivo, bloque.pagina_inicio, bloque.pagina_fin, bloque.texto)

    return Comprobante(
        archivo=bloque.archivo,
        pagina_inicio=bloque.pagina_inicio,
        pagina_fin=bloque.pagina_fin,
        tipo=bloque.tipo_tentativo,
        ruc=ruc,
        ruc_receptor=ruc_receptor,
        razon_social=razon,
        serie_numero=serie,
        fecha=fecha,
        monto_total=monto_total,
        moneda=moneda,
        monto_igv=igv,
        bi_gravado=bi,
        op_exonerada=exo,
        op_inafecta=ina,
        recargo_consumo=rec,
        confianza=conf,
        hash_deduplicacion=clave,
        texto_resumen=_resumen_texto(bloque.texto),
    )


def deduplicar(comprobantes: list[Comprobante]) -> list[Comprobante]:
    """
    Colapsa comprobantes con misma `hash_deduplicacion`. Mantiene el de
    mayor confianza; empata por páginas más tempranas.
    """
    by_key: dict[str, Comprobante] = {}
    for c in comprobantes:
        prev = by_key.get(c.hash_deduplicacion)
        if prev is None:
            by_key[c.hash_deduplicacion] = c
            continue
        mejor = c if c.confianza > prev.confianza else prev
        if c.confianza == prev.confianza and c.pagina_inicio < prev.pagina_inicio:
            mejor = c
        by_key[c.hash_deduplicacion] = mejor
    return list(by_key.values())


def rellenar_desde_ocr_agresivo(
    comprobante: Comprobante,
    pdf_path: str,
) -> list[str]:
    """Segundo intento OCR (alta DPI + preproc agresivo) para rellenar campos
    tributarios vacíos. NO sobrescribe valores ya capturados.

    Devuelve la lista de campos rellenados en esta pasada (para log).
    """
    from ingesta.ocr_region_totales import ocr_pagina_agresivo
    from piloto_field_extract_paso4 import _factura_montos, _recargo_consumo

    campos_clave = ["bi_gravado", "monto_igv", "op_exonerada", "op_inafecta"]
    faltantes = [c for c in campos_clave if getattr(comprobante, c) is None]
    if not faltantes:
        return []

    # Concatenar OCR agresivo de cada página del bloque.
    textos_region: list[str] = []
    for pg in range(comprobante.pagina_inicio, comprobante.pagina_fin + 1):
        try:
            txt, _ = ocr_pagina_agresivo(pdf_path, pg)
            if txt:
                textos_region.append(txt)
        except Exception:
            continue
    if not textos_region:
        return []
    region_text = "\n".join(textos_region)

    # Re-aplicar extracción de montos sobre el texto mejorado.
    try:
        montos, _regla, _lineas = _factura_montos(region_text)
    except Exception:
        return []

    rellenados: list[str] = []
    for campo in faltantes:
        nuevo = montos.get(campo)
        if nuevo is not None and getattr(comprobante, campo) is None:
            setattr(comprobante, campo, nuevo)
            rellenados.append(campo)

    # Recargo al consumo — campo adicional (no bloquea)
    if comprobante.recargo_consumo is None:
        rec = montos.get("recargo_consumo")
        if rec is not None:
            comprobante.recargo_consumo = rec
            rellenados.append("recargo_consumo")

    return rellenados


def extraer_comprobantes(bloques) -> list[Comprobante]:
    """
    Ejecuta extraer_de_bloque + deduplicar. Conveniencia para callers.
    """
    crudos = [extraer_de_bloque(b) for b in bloques]
    return deduplicar(crudos)
