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
    print("[process] aún no implementado (commit 2-4)")
    return 2


def _cmd_export(args: argparse.Namespace) -> int:
    print("[export] aún no implementado (commit 5)")
    return 2


def _cmd_run_all(args: argparse.Namespace) -> int:
    rc = _cmd_scan(args)
    if rc != 0:
        return rc
    rc = _cmd_process(args)
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

    for name in ("scan", "process", "export", "run-all"):
        p = sub.add_parser(name)
        p.add_argument("--src", required=(name in ("scan", "run-all")), type=Path)
        p.add_argument("--expediente-id", type=str, default=None)

    args = ap.parse_args(argv)
    dispatch = {
        "scan": _cmd_scan,
        "process": _cmd_process,
        "export": _cmd_export,
        "run-all": _cmd_run_all,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
