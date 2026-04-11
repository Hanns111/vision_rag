"""
PASO 2 — Bake-off OCR sobre las 15 páginas del piloto (mismas reglas §4.3 / METRICAS_MINIMAS).

Motores:
  - tesseract_baseline: PyMuPDF + Tesseract (document_ocr_runner.process_pdf)
  - docling: DocumentConverter CPU → markdown
  - easyocr: raster 300 DPI + EasyOCR (sustituto operativo si PaddleOCR no corre en el entorno)

Salida: data/piloto_ocr/metrics/bakeoff_paso2_*_YYYYMMDD.csv y resumen + informe.

Uso (recomendado Python 3.11–3.12; ver requirements-paso2.txt):
  python scripts/bakeoff_paso2.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent
_METRICS = _REPO / "data" / "piloto_ocr" / "metrics"
_RAW = _REPO / "data" / "piloto_ocr" / "raw"
_LABELS = _REPO / "data" / "piloto_ocr" / "labels"
_MANIFEST = _REPO / "data" / "piloto_ocr" / "MANIFEST_PILOTO.csv"

_FIELD_KEYS = [
    "ruc_emisor",
    "tipo_documento",
    "serie_numero",
    "fecha_emision",
    "moneda",
    "monto_subtotal",
    "monto_igv",
    "monto_total",
    "ruc_receptor",
    "razon_social_emisor",
]


def _load_pilot_pages() -> list[tuple[str, Path, int]]:
    """Lista (doc_id, pdf_path, page_index 1-based)."""
    out: list[tuple[str, Path, int]] = []
    with open(_MANIFEST, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row["doc_id"].strip()
            rel = row["archivo_raw_relativo"].strip().replace("\\", "/")
            name = rel.split("/")[-1]
            pdf_path = _RAW / name
            if not pdf_path.is_file():
                raise FileNotFoundError(pdf_path)
            raw_indices = row["indices_paginas_en_pdf"].strip().strip('"')
            for part in raw_indices.split(","):
                part = part.strip()
                if not part:
                    continue
                out.append((doc_id, pdf_path, int(part)))
    if len(out) != 15:
        raise RuntimeError(f"Se esperaban 15 páginas piloto, hay {len(out)}")
    return out


def _single_page_pdf(src: Path, page_1based: int, out_path: Path) -> None:
    import fitz

    doc = fitz.open(str(src))
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=page_1based - 1, to_page=page_1based - 1)
    new_doc.save(str(out_path))
    new_doc.close()
    doc.close()


def _page_bgr_300dpi(pdf_path: Path, page_1based: int):
    import cv2
    import fitz
    import numpy as np

    doc = fitz.open(str(pdf_path))
    page = doc.load_page(page_1based - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    elif pix.n == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    doc.close()
    return arr


def _text_baseline(pdf_one: Path) -> str:
    if str(_REPO / "scripts") not in sys.path:
        sys.path.insert(0, str(_REPO / "scripts"))
    from document_ocr_runner import process_pdf

    rows = process_pdf(str(pdf_one))
    if not rows:
        return ""
    return (rows[0].get("texto") or "").strip()


def _docling_converter():
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU, num_threads=4)
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def _text_docling(conv, pdf_one: Path) -> str:
    res = conv.convert(str(pdf_one))
    return (res.document.export_to_markdown() or "").strip()


def _easyocr_reader():
    import easyocr

    return easyocr.Reader(["es", "en"], gpu=False, verbose=False)


def _text_easyocr(reader, pdf_path: Path, page_1based: int) -> str:
    img = _page_bgr_300dpi(pdf_path, page_1based)
    lines = reader.readtext(img)
    return "\n".join(line[1] for line in lines).strip()


def _load_gold(doc_id: str, page_index: int) -> dict[str, Any]:
    p = _LABELS / f"{doc_id}_p{page_index}.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    sys.path.insert(0, str(_REPO / "scripts"))
    from piloto_field_extract_minimal import extract_fields_minimal, gold_pred_match

    run_date = date.today().isoformat()
    ymd = run_date.replace("-", "")
    pages = _load_pilot_pages()

    _METRICS.mkdir(parents=True, exist_ok=True)

    motors: dict[str, Any] = {
        "tesseract_baseline": {"fn": None, "times": []},
        "docling": {"fn": None, "times": [], "conv": None},
        "easyocr_raster": {"fn": None, "times": [], "reader": None},
    }

    motors["docling"]["conv"] = _docling_converter()
    motors["easyocr_raster"]["reader"] = _easyocr_reader()

    def get_text(motor: str, pdf_one: Path, src_pdf: Path, page_idx: int) -> str:
        t0 = time.perf_counter()
        if motor == "tesseract_baseline":
            txt = _text_baseline(pdf_one)
        elif motor == "docling":
            txt = _text_docling(motors["docling"]["conv"], pdf_one)
        elif motor == "easyocr_raster":
            txt = _text_easyocr(motors["easyocr_raster"]["reader"], src_pdf, page_idx)
        else:
            raise ValueError(motor)
        elapsed = time.perf_counter() - t0
        motors[motor]["times"].append(elapsed)
        return txt

    all_rows: dict[str, list[dict[str, Any]]] = {m: [] for m in motors}

    tmpdir = tempfile.mkdtemp(prefix="piloto_paso2_", dir=str(_METRICS))

    try:
        for doc_id, pdf_path, page_idx in pages:
            one_pdf = Path(tmpdir) / f"{doc_id}_p{page_idx}.pdf"
            _single_page_pdf(pdf_path, page_idx, one_pdf)

            gold_j = _load_gold(doc_id, page_idx)
            gold_campos = gold_j["campos"]

            for motor in motors:
                text = get_text(motor, one_pdf, pdf_path, page_idx)
                pred = extract_fields_minimal(text)

                for campo in _FIELD_KEYS:
                    g = gold_campos.get(campo)
                    p = pred.get(campo)
                    if g is None:
                        ex = ""
                    else:
                        ex = 1 if gold_pred_match(campo, g, p) else 0
                    all_rows[motor].append(
                        {
                            "doc_id": doc_id,
                            "page_index": page_idx,
                            "campo": campo,
                            "valor_gold": g if g is not None else "",
                            "valor_pred": p if p is not None else "",
                            "exactitud": ex,
                            "motor": motor,
                            "fecha_corrida": run_date,
                            "len_texto_pagina": len(text),
                        }
                    )
    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)

    # CSV por motor (detalle)
    for motor, rows in all_rows.items():
        out = _METRICS / f"bakeoff_paso2_{motor}_{ymd}.csv"
        if rows:
            keys = list(rows[0].keys())
            with open(out, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                w.writerows(rows)

    # Resumen
    resumen_rows: list[dict[str, Any]] = []
    for motor, rows in all_rows.items():
        evaluated = [r for r in rows if r["exactitud"] != ""]
        correct = sum(1 for r in evaluated if r["exactitud"] == 1)
        n_eval = len(evaluated)
        macro_f1 = (correct / n_eval) if n_eval else 0.0
        t_total = sum(motors[motor]["times"])
        secs_pp = t_total / 15.0
        lens = [rows[i]["len_texto_pagina"] for i in range(0, len(rows), len(_FIELD_KEYS))]
        len_avg = sum(lens) / len(lens) if lens else 0.0
        resumen_rows.append(
            {
                "motor": motor,
                "macro_f1_campos_eval": round(macro_f1, 4),
                "celdas_evaluadas": n_eval,
                "celdas_correctas": correct,
                "tiempo_total_s": round(t_total, 2),
                "segundos_por_pagina": round(secs_pp, 3),
                "len_texto_promedio": round(len_avg, 1),
                "fecha_corrida": run_date,
            }
        )

    res_path = _METRICS / f"bakeoff_paso2_resumen_{ymd}.csv"
    with open(res_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(resumen_rows[0].keys()))
        w.writeheader()
        w.writerows(resumen_rows)

    log_path = _METRICS / f"bakeoff_paso2_run_log_{ymd}.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"bakeoff_paso2 fecha={run_date} paginas=15\n")
        for line in resumen_rows:
            f.write(str(line) + "\n")

    print("OK — archivos en", _METRICS)
    for r in resumen_rows:
        print(r)


if __name__ == "__main__":
    main()
