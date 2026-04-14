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
        from ingesta.comprobante_extractor import extraer_comprobantes
    except Exception:
        detectar_bloques = None
        extraer_comprobantes = None

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


def _cmd_export(args: argparse.Namespace) -> int:
    """Lee extractions/*.json + expediente.json de TODOS los expedientes en `dest`."""
    import json
    from ingesta.excel_export import (
        DocumentoValidacion,
        ExpedienteValidacion,
        CandidatoResolucion,
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

        # expediente.json (schema v2) — resolución de identidad
        exp_json_path = exp_dir / "expediente.json"
        resolucion: dict[str, Any] = {}
        if exp_json_path.exists():
            try:
                resolucion = (json.loads(exp_json_path.read_text(encoding="utf-8")) or {}).get(
                    "resolucion_id"
                ) or {}
            except Exception:
                resolucion = {}

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

    path = exportar_excel(xlsx, documentos, expedientes, candidatos=candidatos_resolucion)
    print(f"[export] xlsx={path}")
    print(
        f"[export] documentos={len(documentos)} expedientes={len(expedientes)} "
        f"candidatos_id={len(candidatos_resolucion)}"
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
