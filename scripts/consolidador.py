"""
Consolidador de expediente → produce `expediente.json` (schema expediente.v2).

Entrada:
  - control_previo/procesados/{exp_id}/metadata.json
  - control_previo/procesados/{exp_id}/extractions/{archivo}.json
      (cada uno con `clasificacion.tipo_detectado` y `resolucion_id.candidatos_en_este_archivo`)

Salida:
  - control_previo/procesados/{exp_id}/expediente.json (schema.v2)

Lógica de scoring (determinista, auditable):
  score(id) = Σ_docs (peso_doc × peso_tipo_id × frecuencia_en_doc)
             + peso_nombre_carpeta × 1 (si aparece en el nombre)

  peso_tipo_id:       sinad=5, exp=4, oficio=3, siaf=2, anio=1, planilla=1, pedido=1
  peso_tipo_documento: rendicion=4, solicitud=3, oficio=3, factura=1,
                       pasaje=1, anexo=2, otros=1, tipo_desconocido=1
  peso_nombre_carpeta: 1 (solo referencia)

Estados por cada campo (expediente, sinad, siaf, anio):
  OK                   : score_max ≥ UMBRAL_MIN y score_max/score_2do ≥ DOMINANCIA_MIN
  CONFLICTO_EXPEDIENTE : score_2do/score_max ≥ 0.5 (dos candidatos fuertes)
  BAJA_CONFIANZA       : score_max < UMBRAL_MIN

`estado_resolucion` del ResolucionId es el PEOR de los 4 (peor manda: CONFLICTO > BAJA > OK).
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from modelo.expediente import (  # noqa: E402
    Expediente,
    IdCandidato,
    ResolucionId,
    FuenteEvidencia,
    Comprobante,
    FlujoFinanciero,
    SCHEMA_VERSION,
)
from ingesta.id_resolver import detectar_candidatos  # noqa: E402


UMBRAL_MIN = 10.0
DOMINANCIA_MIN = 2.0
CONFLICTO_RATIO = 0.5

PESO_TIPO_ID: dict[str, int] = {
    "sinad": 5,
    "exp": 4,
    "oficio": 3,
    "siaf": 2,
    "anio": 1,
    "planilla": 1,
    "pedido": 1,
}

PESO_TIPO_DOCUMENTO: dict[str, int] = {
    "rendicion": 4,
    "solicitud": 3,
    "oficio": 3,
    "anexo": 2,
    "factura": 1,
    "pasaje": 1,
    "orden_servicio": 1,
    "orden_compra": 1,
    "otros": 1,
    "tipo_desconocido": 1,
}

PESO_NOMBRE_CARPETA = 1


def _carpeta_contiene_id(carpeta: str, id_canonico: str, tipo: str) -> bool:
    """
    La carpeta "aporta" un candidato si el número aparece en el nombre
    (ej. carpeta "DIED2026-INT-0250235" contiene SINAD-250235: los dígitos "250235").
    """
    if not carpeta or not id_canonico:
        return False
    try:
        valor = id_canonico.split("-", 1)[1]  # "SINAD-250235" → "250235"
    except IndexError:
        return False
    # numérico: normalizamos ambos sin ceros
    if valor.isdigit():
        valor_sin_ceros = valor.lstrip("0") or "0"
        return valor_sin_ceros in carpeta or valor in carpeta
    return valor in carpeta


def _agg_candidatos_por_expediente(
    docs: list[dict],
    nombre_carpeta: str,
) -> dict[tuple[str, str], IdCandidato]:
    """
    Suma frecuencias y aplica pesos. Clave: (tipo, id_canonico).
    """
    agg: dict[tuple[str, str], IdCandidato] = {}

    for doc in docs:
        archivo = doc.get("archivo", "")
        tipo_doc = (doc.get("clasificacion") or {}).get("tipo_detectado", "tipo_desconocido")
        peso_doc = PESO_TIPO_DOCUMENTO.get(tipo_doc, 1)
        candidatos_doc = (doc.get("resolucion_id") or {}).get("candidatos_en_este_archivo", [])

        for c in candidatos_doc:
            tipo = c.get("tipo", "")
            id_canonico = c.get("id_canonico", "")
            if not tipo or not id_canonico:
                continue
            peso_id = PESO_TIPO_ID.get(tipo, 1)
            freq = int(c.get("frecuencia", 0) or 0)
            contribucion = peso_doc * peso_id * freq

            clave = (tipo, id_canonico)
            if clave not in agg:
                agg[clave] = IdCandidato(
                    id_canonico=id_canonico,
                    tipo=tipo,
                    valor_original=c.get("valor_original", ""),
                    frecuencia=0,
                    score_total=0.0,
                    fuentes=[],
                )
            entry = agg[clave]
            entry.frecuencia += freq
            entry.score_total += contribucion
            # mantener trazabilidad de fuentes por archivo + fragmento
            for fsrc in c.get("fuentes", [])[:3]:
                entry.fuentes.append(
                    FuenteEvidencia(
                        archivo=archivo,
                        pagina=fsrc.get("pagina"),
                        fragmento=(fsrc.get("fragmento") or "")[:200],
                        regla=fsrc.get("regla", ""),
                        tipo_documento=tipo_doc,
                    )
                )

    # Aporte del nombre de carpeta (peso bajo; solo sobre candidatos ya detectados en texto)
    for clave, entry in list(agg.items()):
        if _carpeta_contiene_id(nombre_carpeta, entry.id_canonico, entry.tipo):
            entry.score_total += PESO_NOMBRE_CARPETA
            entry.fuentes.append(
                FuenteEvidencia(
                    archivo="",
                    pagina=None,
                    fragmento=f"nombre_carpeta:{nombre_carpeta}",
                    regla="carpeta_contiene_valor",
                    tipo_documento="",
                )
            )

    return agg


def _resolver_campo(
    candidatos_tipo: list[IdCandidato],
) -> tuple[str | None, float, str, list[str]]:
    """
    Para una lista de candidatos de un mismo tipo, devuelve:
      (valor_ganador | None, confianza, estado, observaciones)
    """
    obs: list[str] = []
    if not candidatos_tipo:
        return None, 0.0, "BAJA_CONFIANZA", ["sin_candidatos"]

    ordenados = sorted(candidatos_tipo, key=lambda c: c.score_total, reverse=True)
    top = ordenados[0]
    segundo_score = ordenados[1].score_total if len(ordenados) > 1 else 0.0

    if top.score_total < UMBRAL_MIN:
        return (
            top.id_canonico,
            round(top.score_total / (top.score_total + 1.0), 3),
            "BAJA_CONFIANZA",
            [f"score_max={top.score_total}<umbral_min={UMBRAL_MIN}"],
        )

    dominancia = top.score_total / segundo_score if segundo_score > 0 else float("inf")
    ratio_inv = segundo_score / top.score_total if top.score_total > 0 else 0.0

    if ratio_inv >= CONFLICTO_RATIO:
        obs.append(
            f"conflicto: top={top.id_canonico}({top.score_total}) "
            f"vs segundo={ordenados[1].id_canonico}({segundo_score})"
        )
        confianza = round(top.score_total / (top.score_total + segundo_score + 1.0), 3)
        return top.id_canonico, confianza, "CONFLICTO_EXPEDIENTE", obs

    if dominancia >= DOMINANCIA_MIN:
        # confianza alta: score relativo a la suma total
        suma = sum(c.score_total for c in ordenados)
        confianza = round(top.score_total / (suma + 1.0), 3)
        return top.id_canonico, confianza, "OK", obs

    # dominancia < DOMINANCIA_MIN pero > conflicto → BAJA_CONFIANZA
    return (
        top.id_canonico,
        round(top.score_total / (top.score_total + segundo_score + 1.0), 3),
        "BAJA_CONFIANZA",
        [f"dominancia={dominancia:.2f}<{DOMINANCIA_MIN}"],
    )


def _peor_estado(estados: list[str]) -> str:
    orden = {"CONFLICTO_EXPEDIENTE": 2, "BAJA_CONFIANZA": 1, "OK": 0}
    peor = "OK"
    for e in estados:
        if orden.get(e, 0) > orden.get(peor, 0):
            peor = e
    return peor


def _solo_valor(id_canonico: str | None) -> str | None:
    if not id_canonico:
        return None
    partes = id_canonico.split("-", 1)
    return partes[1] if len(partes) == 2 else id_canonico


def _elegir_expediente_id_detectado(agg: dict) -> IdCandidato | None:
    """
    El expediente_id principal es el ganador entre ids de tipo
    `sinad`, `exp` u `oficio` (los que funcionan como identificador
    administrativo del expediente completo).
    """
    tipos_elegibles = ("sinad", "exp", "oficio")
    elegibles = [c for (t, _), c in agg.items() if t in tipos_elegibles]
    if not elegibles:
        return None
    return max(elegibles, key=lambda c: c.score_total)


def consolidar(exp_dir: Path | str) -> Expediente:
    """
    Lee un expediente procesado y emite el dataclass Expediente (schema v2).
    No escribe a disco — responsabilidad del caller.
    """
    exp_dir = Path(exp_dir).resolve()
    meta_file = exp_dir / "metadata.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"falta metadata.json en {exp_dir}")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    nombre_carpeta = meta["expediente_id"]

    ext_dir = exp_dir / "extractions"
    docs: list[dict] = []
    for f in sorted(ext_dir.glob("*.json")):
        try:
            docs.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue

    # Agregar candidatos a nivel expediente
    agg = _agg_candidatos_por_expediente(docs, nombre_carpeta)
    por_tipo: dict[str, list[IdCandidato]] = defaultdict(list)
    for (tipo, _), entry in agg.items():
        por_tipo[tipo].append(entry)

    # Resolver cada campo
    elegibles = [
        c for c in agg.values() if c.tipo in ("sinad", "exp", "oficio")
    ]
    exp_det, conf_exp, estado_exp, obs_exp = _resolver_campo(elegibles)
    sinad_det, conf_sinad, estado_sinad, obs_sinad = _resolver_campo(por_tipo.get("sinad", []))
    siaf_det, conf_siaf, estado_siaf, obs_siaf = _resolver_campo(por_tipo.get("siaf", []))
    anio_det, conf_anio, estado_anio, obs_anio = _resolver_campo(por_tipo.get("anio", []))

    # Compatibilidad con expediente_id_carpeta
    coincide = False
    if exp_det:
        coincide = _carpeta_contiene_id(nombre_carpeta, exp_det, "")

    observaciones_globales: list[str] = []
    for tag, xs in (
        ("expediente", obs_exp),
        ("sinad", obs_sinad),
        ("siaf", obs_siaf),
        ("anio", obs_anio),
    ):
        for o in xs:
            observaciones_globales.append(f"{tag}:{o}")

    estado_global = _peor_estado([estado_exp, estado_sinad, estado_siaf, estado_anio])

    # Lista completa de candidatos (ordenada por score desc)
    candidatos_ordenados = sorted(
        agg.values(), key=lambda c: c.score_total, reverse=True
    )

    resolucion = ResolucionId(
        expediente_id_carpeta=nombre_carpeta,
        expediente_id_detectado=exp_det,
        sinad=_solo_valor(sinad_det),
        siaf=_solo_valor(siaf_det),
        anio=_solo_valor(anio_det),
        confianza_expediente=conf_exp,
        confianza_sinad=conf_sinad,
        confianza_siaf=conf_siaf,
        confianza_anio=conf_anio,
        estado_resolucion=estado_global,
        coincide_con_carpeta=coincide,
        candidatos=candidatos_ordenados,
        observaciones=observaciones_globales,
    )

    # --- Comprobantes a nivel expediente (deduplicados entre archivos) ---
    comprobantes_agg: list[Comprobante] = []
    hashes_vistos: set[str] = set()
    for doc in docs:
        for c_raw in (doc.get("comprobantes") or []):
            if not isinstance(c_raw, dict) or "hash_deduplicacion" not in c_raw:
                continue
            h = c_raw.get("hash_deduplicacion", "")
            if h in hashes_vistos:
                continue
            hashes_vistos.add(h)
            comprobantes_agg.append(
                Comprobante(
                    archivo=c_raw.get("archivo", ""),
                    pagina_inicio=int(c_raw.get("pagina_inicio", 0) or 0),
                    pagina_fin=int(c_raw.get("pagina_fin", 0) or 0),
                    tipo=c_raw.get("tipo", "desconocido"),
                    ruc=c_raw.get("ruc"),
                    razon_social=c_raw.get("razon_social"),
                    serie_numero=c_raw.get("serie_numero"),
                    fecha=c_raw.get("fecha"),
                    monto_total=c_raw.get("monto_total"),
                    moneda=c_raw.get("moneda"),
                    monto_igv=c_raw.get("monto_igv"),
                    bi_gravado=c_raw.get("bi_gravado"),
                    op_exonerada=c_raw.get("op_exonerada"),
                    op_inafecta=c_raw.get("op_inafecta"),
                    confianza=float(c_raw.get("confianza", 0.0) or 0.0),
                    hash_deduplicacion=h,
                    texto_resumen=c_raw.get("texto_resumen", ""),
                )
            )

    flujo = _calcular_flujo(comprobantes_agg) if comprobantes_agg else None

    exp = Expediente(
        expediente_id_carpeta=nombre_carpeta,
        schema_version=SCHEMA_VERSION,
        resolucion_id=resolucion,
        documentos_archivos=[d["nombre"] for d in meta.get("documentos", [])],
        validaciones=[
            (doc.get("validaciones") or {}).get("firmas_anexo3")
            for doc in docs
            if (doc.get("validaciones") or {}).get("firmas_anexo3")
        ],
        comprobantes=comprobantes_agg,
        flujo_financiero=flujo,
    )
    return exp


def _calcular_flujo(comprobantes: list[Comprobante]) -> FlujoFinanciero:
    """Agrega totales y detecta inconsistencias mínimas; no inventa."""
    from collections import Counter

    total = 0.0
    monedas: Counter = Counter()
    n_fact = n_bol = n_tic = n_desc = 0
    inconsistencias: list[str] = []

    for c in comprobantes:
        if c.tipo == "factura_electronica":
            n_fact += 1
        elif c.tipo == "boleta_venta":
            n_bol += 1
        elif c.tipo == "ticket":
            n_tic += 1
        else:
            n_desc += 1
        if c.monto_total:
            try:
                total += float(c.monto_total)
                if c.moneda:
                    monedas[c.moneda] += 1
            except (ValueError, TypeError):
                inconsistencias.append(
                    f"monto_no_parseable: {c.archivo}#p{c.pagina_inicio}={c.monto_total}"
                )
        else:
            inconsistencias.append(
                f"sin_monto: {c.archivo}#p{c.pagina_inicio}-{c.pagina_fin} tipo={c.tipo}"
            )

    moneda_dominante = monedas.most_common(1)[0][0] if monedas else ""

    return FlujoFinanciero(
        total_detectado=f"{total:.2f}",
        moneda=moneda_dominante,
        n_comprobantes=len(comprobantes),
        n_facturas=n_fact,
        n_boletas=n_bol,
        n_tickets=n_tic,
        n_desconocidos=n_desc,
        inconsistencias=inconsistencias[:50],  # tope para mantener el json legible
    )


def escribir_expediente_json(exp: Expediente, exp_dir: Path | str) -> Path:
    exp_dir = Path(exp_dir).resolve()
    out = exp_dir / "expediente.json"
    out.write_text(
        json.dumps(exp.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out


if __name__ == "__main__":
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Consolida un expediente → expediente.json")
    ap.add_argument("exp_dir", type=Path, help="Ruta a control_previo/procesados/{id}/")
    args = ap.parse_args()
    expediente = consolidar(args.exp_dir)
    out_path = escribir_expediente_json(expediente, args.exp_dir)
    print(f"OK {out_path}")
    r = expediente.resolucion_id
    if r:
        print(f"  expediente_id_detectado={r.expediente_id_detectado} conf={r.confianza_expediente}")
        print(f"  sinad={r.sinad} conf={r.confianza_sinad}")
        print(f"  siaf={r.siaf} conf={r.confianza_siaf}")
        print(f"  anio={r.anio} conf={r.confianza_anio}")
        print(f"  estado={r.estado_resolucion} coincide_carpeta={r.coincide_con_carpeta}")
