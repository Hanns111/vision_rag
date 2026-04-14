"""
Evaluación PASO 4: extractor por reglas vs gold, usando OCR tesseract congelado (PASO 2).

Salida: data/piloto_ocr/metrics/paso4_eval_linux_wsl/
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_OCR_DIR = _REPO / "data" / "piloto_ocr" / "metrics" / "paso2_linux_wsl" / "tesseract_baseline"
_LABELS = _REPO / "data" / "piloto_ocr" / "labels"
_OUT = _REPO / "data" / "piloto_ocr" / "metrics" / "paso4_eval_linux_wsl"


def _gold_evaluable(gold) -> bool:
    if gold is None:
        return False
    if isinstance(gold, str) and not gold.strip():
        return False
    return True


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    sys.path.insert(0, str(_REPO / "scripts"))
    from piloto_field_extract_minimal import extract_fields_minimal, gold_pred_match
    from piloto_field_extract_paso4 import extract_fields_paso4, field_keys

    _OUT.mkdir(parents=True, exist_ok=True)
    keys = field_keys()
    run_date = date.today().isoformat()
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

    rows: list[dict] = []
    summary_min = defaultdict(int)  # campo -> aciertos
    summary_p4 = defaultdict(int)
    total_eval = defaultdict(int)

    txt_files = sorted(_OCR_DIR.glob("*.txt"))
    if not txt_files:
        raise SystemExit(f"No hay .txt en {_OCR_DIR}")

    traces_out: list[dict] = []

    for p in txt_files:
        m = re.match(r"^(.+)_p(\d+)\.txt$", p.name)
        if not m:
            continue
        doc_id, pidx = m.group(1), int(m.group(2))
        label_path = _LABELS / f"{doc_id}_p{pidx}.json"
        if not label_path.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        gold_j = json.loads(label_path.read_text(encoding="utf-8"))
        gold_c = gold_j["campos"]

        f_min = extract_fields_minimal(text)
        f_p4, trace = extract_fields_paso4(text)

        rec_trace = {
            "archivo_ocr": str(p.relative_to(_REPO)),
            "doc_id": doc_id,
            "page_index": pidx,
            "trace_por_campo": trace,
        }
        traces_out.append(rec_trace)

        for campo in keys:
            gv = gold_c.get(campo)
            if not _gold_evaluable(gv):
                continue
            total_eval[campo] += 1
            ok_m = gold_pred_match(campo, gv, f_min.get(campo))
            ok_p = gold_pred_match(campo, gv, f_p4.get(campo))
            if ok_m:
                summary_min[campo] += 1
            if ok_p:
                summary_p4[campo] += 1
            tr = trace.get(campo, {})
            rows.append(
                {
                    "doc_id": doc_id,
                    "page_index": pidx,
                    "campo": campo,
                    "gold": gv if gv is not None else "",
                    "pred_minimal": f_min.get(campo) if f_min.get(campo) is not None else "",
                    "pred_paso4": f_p4.get(campo) if f_p4.get(campo) is not None else "",
                    "ok_minimal": "1" if ok_m else "0",
                    "ok_paso4": "1" if ok_p else "0",
                    "delta_ok": str(int(ok_p) - int(ok_m)),
                    "regla_paso4": tr.get("regla") or "",
                    "tipo_doc_inferido": tr.get("tipo_doc_inferido") or "",
                }
            )

    csv_path = _OUT / f"paso4_eval_detalle_{run_date.replace('-', '')}.csv"
    if rows:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    json_trace_path = _OUT / f"paso4_eval_trazas_{run_date.replace('-', '')}.json"
    json_trace_path.write_text(json.dumps(traces_out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Resumen por campo
    res_lines = [
        "| campo | evaluables | ok minimal | ok PASO4 | mejora |",
        "|-------|------------|------------|----------|--------|",
    ]
    mejoras_tot = 0
    regresiones = 0
    for campo in keys:
        te = total_eval[campo]
        if te == 0:
            continue
        om = summary_min[campo]
        op = summary_p4[campo]
        mej = op - om
        if mej > 0:
            mejoras_tot += mej
        if mej < 0:
            regresiones -= mej
        res_lines.append(f"| {campo} | {te} | {om} | {op} | {mej:+d} |")

    md_path = _OUT / f"INFORME_PASO4_EVAL_{run_date.replace('-', '')}.md"
    md_path.write_text(
        "\n".join(
            [
                f"# PASO 4 — Evaluación vs extractor mínimo ({run_date})",
                "",
                f"Generado: {ts}",
                "",
                "OCR fuente: `data/piloto_ocr/metrics/paso2_linux_wsl/tesseract_baseline/*.txt`",
                "",
                "## Resumen por campo",
                "",
                *res_lines,
                "",
                f"- **Mejoras netas (suma de deltas por campo):** {mejoras_tot}",
                f"- **Regresiones (fallos nuevos vs minimal):** {regresiones}",
                "",
                "## Archivos",
                "",
                f"- Detalle CSV: `{csv_path.relative_to(_REPO)}`",
                f"- Trazas JSON: `{json_trace_path.relative_to(_REPO)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print("OK", _OUT)
    print("CSV:", csv_path)
    print("JSON trazas:", json_trace_path)
    print("MD:", md_path)


if __name__ == "__main__":
    main()
