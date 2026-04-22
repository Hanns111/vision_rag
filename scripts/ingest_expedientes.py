"""
CLI de ingesta + clasificación + extracción + Excel de validación.

Subcomandos:
  scan      Copia PDFs a `control_previo/procesados/{id}/source/` y genera metadata.json
  process   Lee texto (PyMuPDF/OCR), clasifica, extrae campos, escribe extractions/*.json
  export    Consolida extractions/*.json en `data/piloto_ocr/metrics/validacion_expedientes.xlsx`
  run-all   scan + process + export en una sola corrida

Uso típico:
  python scripts/ingest_expedientes.py run-all --src DIED2026-INT-0250235
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO / "scripts"))

_DEFAULT_DEST = _REPO / "control_previo" / "procesados"
_DEFAULT_XLSX = _REPO / "data" / "piloto_ocr" / "metrics" / "validacion_expedientes.xlsx"


def _cmd_scan(args: argparse.Namespace) -> int:
    from ingesta.scanner import ingest_expediente

    src = Path(args.src).resolve()
    dest = Path(args.dest).resolve()
    res = ingest_expediente(src, dest, expediente_id=args.expediente_id)
    print(f"[scan] expediente_id={res.expediente_id} docs={len(res.documentos)}")
    print(f"[scan] destino={res.ruta_destino}")
    for d in res.documentos:
        print(f"  - {d.nombre} paginas={d.paginas} sha1={d.sha1[:12]}...")
    return 0


def _cmd_process(args: argparse.Namespace) -> int:
    """Lee texto → clasifica → extrae → resolver_id → valida → escribe extractions/{archivo}.json."""
    import json
    from dataclasses import asdict
    from ingesta.text_reader import read_pdf_with_cache
    from ingesta.classifier import classify
    from ingesta.extractor import extract_campos
    try:
        from validaciones.firmas_anexo3 import validar as validar_firmas
    except Exception:  # validación opcional; si falta el módulo, el pipeline sigue
        validar_firmas = None
    try:
        from ingesta.id_resolver import detectar_candidatos
    except Exception:
        detectar_candidatos = None
    try:
        from ingesta.comprobante_detector import detectar_bloques
        from ingesta.comprobante_extractor import (
            extraer_comprobantes,
            rellenar_desde_ocr_agresivo,
        )
    except Exception:
        detectar_bloques = None
        extraer_comprobantes = None
        rellenar_desde_ocr_agresivo = None

    dest = Path(args.dest).resolve()
    exp_id = args.expediente_id or (Path(args.src).name if args.src else None)
    if not exp_id:
        print("[process] --expediente-id o --src requerido")
        return 2
    exp_dir = dest / exp_id
    meta_file = exp_dir / "metadata.json"
    if not meta_file.exists():
        print(f"[process] falta metadata.json: {meta_file} (corre `scan` primero)")
        return 2

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    cache_dir = exp_dir / "ocr_cache"
    extractions_dir = exp_dir / "extractions"
    extractions_dir.mkdir(exist_ok=True)

    for d in meta["documentos"]:
        src_pdf = Path(d["ruta_destino"])
        nombre = d["nombre"]
        print(f"[process] {nombre}...", flush=True)

        try:
            txt_meta = read_pdf_with_cache(src_pdf, d["sha1"], cache_dir, force=args.force)
            texto = Path(txt_meta.texto_concatenado_path).read_text(
                encoding="utf-8", errors="replace"
            )
        except Exception as exc:
            estado = "error"
            error_msg = f"lectura:{exc!s}"
            payload = {
                "archivo": nombre,
                "expediente_id": exp_id,
                "estado_procesamiento": estado,
                "error": error_msg,
            }
            (extractions_dir / f"{nombre}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[process]   ERROR lectura: {exc!s}")
            continue

        cls = classify(texto, nombre)
        ext = extract_campos(texto, cls.tipo_detectado)

        if cls.tipo_detectado == "tipo_desconocido":
            estado = "bajo_confianza"
        elif cls.confianza < 0.5:
            estado = "bajo_confianza"
        else:
            estado = "ok"

        # Resolución de identidad (SINAD, SIAF, EXP, AÑO) — desacoplada, aditiva.
        resolucion_id_doc: dict[str, Any] | None = None
        if detectar_candidatos is not None and not args.skip_resolucion:
            try:
                cands = detectar_candidatos(texto, nombre)
                resolucion_id_doc = {
                    "candidatos_en_este_archivo": [c.to_dict() for c in cands]
                }
            except Exception as exc:
                resolucion_id_doc = {
                    "candidatos_en_este_archivo": [],
                    "error": f"excepcion:{exc!s}",
                }

        # Detección + extracción de comprobantes (solo rendiciones por ahora).
        comprobantes_doc: list[dict[str, Any]] | None = None
        if (
            detectar_bloques is not None
            and not args.skip_comprobantes
            and cls.tipo_detectado == "rendicion"
        ):
            try:
                bloques = detectar_bloques(texto, nombre)
                comps = extraer_comprobantes(bloques)

                # --- Segunda pasada OCR agresivo para comprobantes con campos
                # tributarios faltantes (bi/igv/exo/ina). Solo rellena huecos,
                # nunca sobrescribe. Costo: ~3-6s por comprobante candidato.
                if rellenar_desde_ocr_agresivo is not None and not args.skip_ocr_agresivo:
                    pdf_abs = str(src_pdf)
                    for c in comps:
                        campos_clave = ("bi_gravado", "monto_igv",
                                        "op_exonerada", "op_inafecta")
                        if any(getattr(c, k) is None for k in campos_clave):
                            rellenados = rellenar_desde_ocr_agresivo(c, pdf_abs)
                            if rellenados:
                                print(
                                    f"[process]     ocr_agresivo p{c.pagina_inicio}-{c.pagina_fin} "
                                    f"({c.serie_numero or '-'}) rellenó: {','.join(rellenados)}",
                                    flush=True,
                                )

                comprobantes_doc = [c.to_dict() for c in comps]
            except Exception as exc:
                comprobantes_doc = [{"error": f"excepcion:{exc!s}"}]

        # Validación de firmas en Anexo 3: solo sobre rendiciones, desacoplada.
        # Si falla el módulo o el archivo no es rendición → validaciones=null.
        validaciones_out: dict[str, Any] | None = None
        if (
            validar_firmas is not None
            and not args.skip_validaciones
            and cls.tipo_detectado == "rendicion"
        ):
            try:
                v = validar_firmas(texto)
                validaciones_out = {"firmas_anexo3": v.to_dict()}
            except Exception as exc:
                validaciones_out = {
                    "firmas_anexo3": {
                        "tipo_validacion": "firmas_anexo3",
                        "estado": "INSUFICIENTE_EVIDENCIA",
                        "errores": [f"excepcion:{exc!s}"],
                        "confianza": 0.0,
                        "firmantes": [],
                        "nota": "error_ejecucion_validador",
                    }
                }

        payload = {
            "archivo": nombre,
            "expediente_id": exp_id,
            "sha1": d["sha1"],
            "ruta_origen": d["ruta_origen"],
            "ruta_destino": d["ruta_destino"],
            "paginas": d["paginas"],
            "lectura": {
                "len_total": txt_meta.len_total,
                "paginas_con_texto": txt_meta.paginas_con_texto,
                "motores": sorted({p.motor for p in txt_meta.paginas}),
            },
            "clasificacion": {
                "tipo_detectado": cls.tipo_detectado,
                "confianza": cls.confianza,
                "subtipos_detectados": cls.subtipos_detectados,
                "nota": cls.nota,
                "puntajes": cls.puntajes,
                "reglas_activadas": [
                    {"regla": r.regla, "peso": r.peso, "fragmento": r.fragmento}
                    for r in cls.reglas_activadas
                ],
            },
            "extraccion": {
                "tipo_doc_interno": ext.tipo_doc_interno,
                "monto": asdict(ext.monto),
                "fecha": asdict(ext.fecha),
                "ruc": asdict(ext.ruc),
                "razon_social": asdict(ext.razon_social),
                "numero_documento": asdict(ext.numero_documento),
                "tipo_gasto": asdict(ext.tipo_gasto),
                "texto_resumen": ext.texto_resumen,
            },
            "resolucion_id": resolucion_id_doc,
            "comprobantes": comprobantes_doc,
            "validaciones": validaciones_out,
            "estado_procesamiento": estado,
        }
        (extractions_dir / f"{nombre}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        n_comp = len(comprobantes_doc) if comprobantes_doc else 0
        print(
            f"[process]   tipo={cls.tipo_detectado} conf={cls.confianza} "
            f"estado={estado} subtipos={cls.subtipos_detectados or '-'} "
            f"comprobantes={n_comp}"
        )
    return 0


def _cargar_extractions(exp_dir: Path) -> list[dict]:
    import json

    out: list[dict] = []
    for f in sorted((exp_dir / "extractions").glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _clasificar_tipo_tributario(
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


def _evaluar_consistencia(
    monto_total: str | None,
    bi_gravado: str | None,
    monto_igv: str | None,
    op_exonerada: str | None,
    op_inafecta: str | None,
    recargo_consumo: str | None,
) -> tuple[str, str]:
    """Valida que monto_total ≈ bi + igv + exo + ina + recargo (±1.00), con
    jerarquía conceptual tributaria.

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
                             (no hay cómo validar)
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
        return "DATOS_INSUFICIENTES", "falta monto_total"
    if not presentes:
        return "DATOS_INSUFICIENTES", "monto_total presente pero todos los componentes vacios"

    # Si todos los componentes capturados son 0 y total > 0, no hay breakdown
    # real — el desglose tributario del PDF no se capturó (OCR roto o boleta
    # simplificada sin tabla de totales). No es contradicción, es gap.
    if total > 0.01 and all((v is None or v < 0.01) for v in comps.values()):
        return (
            "DATOS_INSUFICIENTES",
            "desglose tributario no capturado (todos los componentes 0 o vacíos)",
        )

    tipo, esperados = _clasificar_tipo_tributario(
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
        motivos.append(f"faltan componentes esperados ({tipo}): {','.join(ausentes_relevantes)}")

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
    return estado, detalle


def _clasificadores_gasto_expediente(exp_dir: Path) -> list[str]:
    """Extrae los clasificadores MEF presentes en los documentos de planilla/
    solicitud del expediente. Lectura directa del cache OCR — sin LLM, regex
    determinista.

    Formato tolerado (observado en real): '2.3.2 1.2 1', '2.3. 2 1. 2 1',
    '2.3.2 7.11 99'. Se normaliza a 'X.Y.Z A.BB CC' con un solo espacio.
    """
    import re

    cache = exp_dir / "ocr_cache"
    if not cache.exists():
        return []
    found: set[str] = set()
    # Patrón determinista: anclado a "2.3." que es el grupo genérico de
    # "BIENES Y SERVICIOS" en el clasificador MEF para gasto corriente.
    pat = re.compile(
        r"\b2\s*\.\s*3\s*\.\s*(\d)\s+(\d)\s*\.\s*(\d{1,2})\s+(\d{1,2})\b"
    )
    for txt_file in cache.glob("*.txt"):
        try:
            t = txt_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "CADENA FUNCIONAL" not in t.upper() and "CLASIF" not in t.upper():
            continue
        for m in pat.finditer(t):
            code = f"2.3.{m.group(1)} {m.group(2)}.{m.group(3)} {m.group(4)}"
            found.add(code)
    return sorted(found)


def _cmd_export(args: argparse.Namespace) -> int:
    """Lee extractions/*.json + expediente.json de TODOS los expedientes en `dest`."""
    import json
    from ingesta.excel_export import (
        DocumentoValidacion,
        ExpedienteValidacion,
        CandidatoResolucion,
        ComprobanteExcel,
        exportar_excel,
    )

    dest = Path(args.dest).resolve()
    xlsx = Path(args.xlsx).resolve()
    if not dest.exists():
        print(f"[export] no existe {dest}")
        return 2

    documentos: list[DocumentoValidacion] = []
    expedientes: list[ExpedienteValidacion] = []
    candidatos_resolucion: list[CandidatoResolucion] = []
    comprobantes_excel: list[ComprobanteExcel] = []

    # filtrar por expediente_id si se pidió, o todos los subdirs
    if args.expediente_id:
        exp_dirs = [dest / args.expediente_id]
    elif args.src:
        exp_dirs = [dest / Path(args.src).name]
    else:
        exp_dirs = [p for p in sorted(dest.iterdir()) if p.is_dir()]

    for exp_dir in exp_dirs:
        meta_file = exp_dir / "metadata.json"
        if not meta_file.exists():
            continue
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        docs = _cargar_extractions(exp_dir)
        if not docs:
            continue

        # expediente.json (schema v2/v3) — resolución de identidad + comprobantes
        exp_json_path = exp_dir / "expediente.json"
        resolucion: dict[str, Any] = {}
        comprobantes_exp: list[dict[str, Any]] = []
        if exp_json_path.exists():
            try:
                exp_json = json.loads(exp_json_path.read_text(encoding="utf-8")) or {}
                resolucion = exp_json.get("resolucion_id") or {}
                comprobantes_exp = exp_json.get("comprobantes") or []
            except Exception:
                resolucion = {}

        # Clasificadores MEF del expediente (propagados a todas las filas
        # porque viven a nivel de planilla/solicitud, no por comprobante).
        clasifs_exp = _clasificadores_gasto_expediente(exp_dir)
        clasifs_str = "; ".join(clasifs_exp)

        for c in comprobantes_exp:
            estado_cons, detalle_cons = _evaluar_consistencia(
                c.get("monto_total"),
                c.get("bi_gravado"),
                c.get("monto_igv"),
                c.get("op_exonerada"),
                c.get("op_inafecta"),
                c.get("recargo_consumo"),
            )
            # Extraer tipo_tributario del detalle ("tipo=GRAVADA; ..."),
            # sin tocar la función de validación.
            import re as _re
            m_tipo = _re.search(r"tipo=([A-Z_]+)", detalle_cons or "")
            tipo_trib = m_tipo.group(1) if m_tipo else ""
            flag_rev = "SI" if estado_cons in ("DIFERENCIA_CRITICA", "DATOS_INSUFICIENTES") else ""

            comprobantes_excel.append(
                ComprobanteExcel(
                    expediente_id=meta["expediente_id"],
                    archivo=c.get("archivo", ""),
                    pagina_inicio=int(c.get("pagina_inicio", 0) or 0),
                    pagina_fin=int(c.get("pagina_fin", 0) or 0),
                    tipo=c.get("tipo", ""),
                    ruc=c.get("ruc") or "",
                    razon_social=c.get("razon_social") or "",
                    serie_numero=c.get("serie_numero") or "",
                    fecha=c.get("fecha") or "",
                    monto_total=c.get("monto_total") or "",
                    moneda=c.get("moneda") or "",
                    monto_igv=c.get("monto_igv") or "",
                    bi_gravado=c.get("bi_gravado") or "",
                    op_exonerada=c.get("op_exonerada") or "",
                    op_inafecta=c.get("op_inafecta") or "",
                    recargo_consumo=c.get("recargo_consumo") or "",
                    confianza=c.get("confianza", ""),
                    texto_resumen=(c.get("texto_resumen") or "")[:4000],
                    estado_consistencia=estado_cons,
                    tipo_tributario=tipo_trib,
                    flag_revision_manual=flag_rev,
                    detalle_inconsistencia=detalle_cons,
                    clasificadores_gasto_expediente=clasifs_str,
                )
            )

        ganador_id = resolucion.get("expediente_id_detectado") or ""
        sinad_v = resolucion.get("sinad") or ""
        siaf_v = resolucion.get("siaf") or ""
        anio_v = resolucion.get("anio") or ""
        conf_exp = resolucion.get("confianza_expediente", "")
        conf_sinad = resolucion.get("confianza_sinad", "")
        conf_siaf = resolucion.get("confianza_siaf", "")
        estado_res = resolucion.get("estado_resolucion", "")
        es_conflicto = "Sí" if estado_res == "CONFLICTO_EXPEDIENTE" else "No" if estado_res else ""
        coincide = resolucion.get("coincide_con_carpeta", False)
        obs_res = resolucion.get("observaciones") or []
        obs_res_str = "; ".join(str(o) for o in obs_res)[:500]

        # poblar hoja resolucion_ids
        for c in (resolucion.get("candidatos") or []):
            fuentes_c = c.get("fuentes") or []
            fuentes_resumen = "; ".join(
                f"{f.get('archivo') or 'carpeta'}:p{f.get('pagina') or '-'}"
                for f in fuentes_c[:5]
            )
            candidatos_resolucion.append(
                CandidatoResolucion(
                    expediente_carpeta=resolucion.get("expediente_id_carpeta", ""),
                    id_canonico=c.get("id_canonico", ""),
                    tipo=c.get("tipo", ""),
                    frecuencia=int(c.get("frecuencia", 0) or 0),
                    score_total=float(c.get("score_total", 0.0) or 0.0),
                    coincide_con_carpeta="Sí" if coincide and c.get("id_canonico") == ganador_id else "No",
                    es_ganador="Sí" if c.get("id_canonico") == ganador_id else "No",
                    estado_resolucion=estado_res,
                    fuentes=fuentes_resumen,
                )
            )

        n_ok = sum(1 for d in docs if d.get("estado_procesamiento") == "ok")
        n_bc = sum(1 for d in docs if d.get("estado_procesamiento") == "bajo_confianza")
        n_er = sum(1 for d in docs if d.get("estado_procesamiento") == "error")
        tipos = sorted(
            {
                d.get("clasificacion", {}).get("tipo_detectado", "")
                for d in docs
                if d.get("clasificacion")
            }
        )

        expedientes.append(
            ExpedienteValidacion(
                expediente_id=meta["expediente_id"],
                ruta_origen=meta["ruta_origen"],
                ruta_destino=meta["ruta_destino"],
                n_documentos=len(docs),
                n_ok=n_ok,
                n_bajo_confianza=n_bc,
                n_error=n_er,
                tipos_detectados=", ".join(t for t in tipos if t),
                fecha_ingesta=meta.get("fecha_ingesta", ""),
            )
        )

        for d in docs:
            cls = d.get("clasificacion", {}) or {}
            ext = d.get("extraccion", {}) or {}
            def _v(k: str) -> Any:
                c = ext.get(k) or {}
                return c.get("valor") if isinstance(c, dict) else None

            nota = cls.get("nota", "") or ""
            if d.get("estado_procesamiento") == "error":
                nota = f"error: {d.get('error', '')}"

            # Validaciones normativas (opcional; N/A si el archivo no se validó)
            val = (d.get("validaciones") or {}).get("firmas_anexo3") or {}
            val_firmas_nombre = val.get("tipo_validacion", "") if val else ""
            val_estado = val.get("estado", "") if val else ""
            val_errores_lista = val.get("errores", []) if val else []
            val_errores = "; ".join(val_errores_lista) if val_errores_lista else ""
            val_confianza: float | str = val.get("confianza", "") if val else ""

            documentos.append(
                DocumentoValidacion(
                    expediente_id=d.get("expediente_id", ""),
                    archivo=d.get("archivo", ""),
                    ruta_origen=d.get("ruta_origen", ""),
                    tipo_documento_detectado=cls.get("tipo_detectado", "tipo_desconocido"),
                    confianza_tipo=float(cls.get("confianza", 0.0) or 0.0),
                    monto_detectado=_v("monto"),
                    fecha_detectada=_v("fecha"),
                    ruc_detectado=_v("ruc"),
                    razon_social_detectada=_v("razon_social"),
                    numero_documento_detectado=_v("numero_documento"),
                    tipo_gasto_detectado=_v("tipo_gasto"),
                    texto_extraido_resumen=(ext.get("texto_resumen") or "")[:1000],
                    estado_procesamiento=d.get("estado_procesamiento", "error"),
                    nota_sistema=nota,
                    validacion_firmas=val_firmas_nombre,
                    estado_firmas=val_estado,
                    errores_firmas=val_errores,
                    confianza_firmas=val_confianza,
                    expediente_detectado=ganador_id,
                    sinad_detectado=sinad_v,
                    siaf_detectado=siaf_v,
                    anio_detectado=anio_v,
                    confianza_expediente=conf_exp,
                    confianza_sinad=conf_sinad,
                    confianza_siaf=conf_siaf,
                    conflicto_expediente=es_conflicto,
                    observaciones_expediente=obs_res_str,
                )
            )

    path = exportar_excel(
        xlsx,
        documentos,
        expedientes,
        candidatos=candidatos_resolucion,
        comprobantes=comprobantes_excel,
    )
    print(f"[export] xlsx={path}")
    print(
        f"[export] documentos={len(documentos)} expedientes={len(expedientes)} "
        f"candidatos_id={len(candidatos_resolucion)} comprobantes={len(comprobantes_excel)}"
    )
    return 0


def _cmd_consolidate(args: argparse.Namespace) -> int:
    """Produce control_previo/procesados/{id}/expediente.json (schema v2)."""
    from consolidador import consolidar, escribir_expediente_json

    dest = Path(args.dest).resolve()
    exp_id = args.expediente_id or (Path(args.src).name if args.src else None)
    if not exp_id:
        print("[consolidate] --expediente-id o --src requerido")
        return 2
    exp_dir = dest / exp_id
    if not (exp_dir / "metadata.json").exists():
        print(f"[consolidate] falta metadata.json en {exp_dir}")
        return 2
    try:
        expediente = consolidar(exp_dir)
        out = escribir_expediente_json(expediente, exp_dir)
    except Exception as exc:
        print(f"[consolidate] ERROR {exc!s}")
        return 2
    r = expediente.resolucion_id
    print(f"[consolidate] {out}")
    if r:
        print(
            f"[consolidate]   exp={r.expediente_id_detectado} sinad={r.sinad} "
            f"siaf={r.siaf} anio={r.anio} estado={r.estado_resolucion}"
        )
    return 0


def _cmd_run_all(args: argparse.Namespace) -> int:
    rc = _cmd_scan(args)
    if rc != 0:
        return rc
    rc = _cmd_process(args)
    if rc != 0:
        return rc
    if not args.skip_resolucion:
        rc = _cmd_consolidate(args)
        if rc != 0:
            return rc
    return _cmd_export(args)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Ingesta expedientes → Excel validación")
    ap.add_argument(
        "--dest",
        type=Path,
        default=_DEFAULT_DEST,
        help=f"raíz de procesados (default: {_DEFAULT_DEST.relative_to(_REPO)})",
    )
    ap.add_argument("--xlsx", type=Path, default=_DEFAULT_XLSX, help="ruta Excel salida")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("scan", "process", "consolidate", "export", "run-all"):
        p = sub.add_parser(name)
        p.add_argument("--src", required=(name in ("scan", "run-all")), type=Path)
        p.add_argument("--expediente-id", type=str, default=None)
        p.add_argument(
            "--force",
            action="store_true",
            help="reprocesar ignorando cache (aplica a process/run-all)",
        )
        p.add_argument(
            "--skip-validaciones",
            action="store_true",
            help="omitir validaciones normativas (ej. firmas_anexo3)",
        )
        p.add_argument(
            "--skip-resolucion",
            action="store_true",
            help="omitir resolución de identidad (SINAD/SIAF/EXP/AÑO)",
        )
        p.add_argument(
            "--skip-comprobantes",
            action="store_true",
            help="omitir detección/extracción de comprobantes",
        )
        p.add_argument(
            "--skip-ocr-agresivo",
            action="store_true",
            help="omitir segunda pasada OCR agresivo para rellenar campos faltantes",
        )

    args = ap.parse_args(argv)
    dispatch = {
        "scan": _cmd_scan,
        "process": _cmd_process,
        "consolidate": _cmd_consolidate,
        "export": _cmd_export,
        "run-all": _cmd_run_all,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
