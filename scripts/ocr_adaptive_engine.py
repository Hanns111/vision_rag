"""
Motor OCR adaptativo: gating + fallback (Tesseract baseline → Docling CPU → EasyOCR).

Capa encima de `document_ocr_runner.process_pdf` sin modificar su interfaz.
Auditable: logs en `data/piloto_ocr/logs/` y métricas por página.

Requisitos: mismos que PASO 1 + PASO 2 (pymupdf, pytesseract, docling, easyocr, opencv, numpy).
Python 3.11–3.12 recomendado.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Rutas por defecto (repo vision_rag)
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent.parent
_DEFAULT_LOG_DIR = _REPO / "data" / "piloto_ocr" / "logs"
_DEFAULT_LOG_FILE = _DEFAULT_LOG_DIR / "ocr_adaptive_log.txt"
_DEFAULT_METRICS_FILE = _DEFAULT_LOG_DIR / "ocr_adaptive_metrics.jsonl"

_LOG = logging.getLogger(__name__)
if not _LOG.handlers:
    _LOG.addHandler(logging.NullHandler())


@dataclass
class AdaptiveOcrConfig:
    """Umbrales y flags ajustables (ver docstring del módulo)."""

    # Gating: longitud mínima de texto (caracteres) para no considerar "corto"
    min_text_len: int = 500
    # Campos no nulos del extractor mínimo por debajo del cual se sospecha baja calidad
    min_nonnull_fields: int = 2
    # Ratio máximo aceptable de "basura" (caracteres fuera de conjunto permitido / len)
    max_garbage_ratio: float = 0.12
    # Activar motores de respaldo
    enable_docling: bool = True
    enable_easyocr: bool = True
    # Hilos Docling (CPU)
    docling_cpu_threads: int = 4
    # DPI raster EasyOCR (alineado a document_ocr_runner OCR)
    easyocr_dpi: int = 300
    # Idiomas EasyOCR
    easyocr_langs: tuple[str, ...] = ("es", "en")


@dataclass
class _RuntimeEngines:
    """Instancias pesadas (lazy)."""

    docling_converter: Any | None = None
    easyocr_reader: Any | None = None


def _ensure_scripts_path() -> None:
    p = str(Path(__file__).resolve().parent)
    if p not in sys.path:
        sys.path.insert(0, p)


def _single_page_pdf(src: Path, page_1based: int, out_path: Path) -> None:
    import fitz

    doc = fitz.open(str(src))
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=page_1based - 1, to_page=page_1based - 1)
    new_doc.save(str(out_path))
    new_doc.close()
    doc.close()


def _text_baseline_one_page(pdf_one: Path) -> tuple[str, str]:
    """Una página → texto + status (mismo criterio que process_pdf)."""
    _ensure_scripts_path()
    from document_ocr_runner import process_pdf

    rows = process_pdf(str(pdf_one))
    if not rows:
        return "", "sin_resultado"
    r0 = rows[0]
    return (r0.get("texto") or "").strip(), str(r0.get("status") or "")


def _get_docling_converter(cfg: AdaptiveOcrConfig):
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    opts = PdfPipelineOptions()
    opts.accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.CPU, num_threads=cfg.docling_cpu_threads
    )
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def _text_docling(conv: Any, pdf_one: Path) -> str:
    res = conv.convert(str(pdf_one))
    return (res.document.export_to_markdown() or "").strip()


def _get_easyocr_reader(cfg: AdaptiveOcrConfig):
    import easyocr

    return easyocr.Reader(list(cfg.easyocr_langs), gpu=False, verbose=False)


def _page_bgr_dpi(pdf_path: Path, page_1based: int, dpi: int):
    import cv2
    import fitz
    import numpy as np

    doc = fitz.open(str(pdf_path))
    page = doc.load_page(page_1based - 1)
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    elif pix.n == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    doc.close()
    return arr


def _text_easyocr(reader: Any, pdf_path: Path, page_1based: int, dpi: int) -> str:
    img = _page_bgr_dpi(pdf_path, page_1based, dpi)
    lines = reader.readtext(img)
    return "\n".join(line[1] for line in lines).strip()


# Caracteres "útiles" para peruanos / facturas (heurística conservadora)
_GARBAGE_PATTERN = re.compile(
    r"[^\w\s\.,;:/°\-–—€$%()\[\]@#&+=*\"'«»¿?¡!ÑÁÉÍÓÚÜáéíóúüñ]"
)


def garbage_ratio(text: str) -> float:
    if not text:
        return 1.0
    bad = len(_GARBAGE_PATTERN.findall(text))
    return min(1.0, bad / max(len(text), 1))


def count_nonnull_fields(text: str) -> int:
    _ensure_scripts_path()
    from piloto_field_extract_minimal import extract_fields_minimal

    d = extract_fields_minimal(text)
    return sum(1 for v in d.values() if v is not None and str(v).strip() != "")


def gating_motives(text: str, cfg: AdaptiveOcrConfig) -> list[str]:
    """Razones por las que el texto se considera de baja calidad (vacío = OK)."""
    reasons: list[str] = []
    if not text or not text.strip():
        reasons.append("texto_vacio")
        return reasons
    n = len(text)
    if n < cfg.min_text_len:
        reasons.append(f"len<{cfg.min_text_len}")
    gr = garbage_ratio(text)
    if gr > cfg.max_garbage_ratio:
        reasons.append(f"basura>{cfg.max_garbage_ratio:.2f}({gr:.2f})")
    fields = count_nonnull_fields(text)
    if fields < cfg.min_nonnull_fields:
        reasons.append(f"campos<{cfg.min_nonnull_fields}({fields})")
    return reasons


def needs_fallback(text: str, cfg: AdaptiveOcrConfig) -> bool:
    return bool(gating_motives(text, cfg))


def quality_score(text: str) -> float:
    """
    Puntuación para elegir el mejor candidato entre motores (mayor = mejor).
    Heurística: longitud + campos útiles - penalización por basura.
    """
    if not text:
        return -1.0
    _ensure_scripts_path()
    from piloto_field_extract_minimal import extract_fields_minimal

    d = extract_fields_minimal(text)
    fn = sum(1 for v in d.values() if v is not None and str(v).strip() != "")
    gr = garbage_ratio(text)
    return float(len(text)) * 0.5 + fn * 80.0 - gr * 2000.0


def _ts_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _append_log_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def _append_metrics_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_pdf_adaptive(
    pdf_path: Path | str,
    *,
    config: AdaptiveOcrConfig | None = None,
    log_file: Path | None = None,
    metrics_file: Path | None = None,
    write_logs: bool = True,
) -> list[dict[str, Any]]:
    """
    Procesa un PDF completo página a página con gating y fallback.

    Devuelve una lista de dicts compatible con `document_ocr_runner.process_pdf`
    (claves `pagina`, `status`, `texto`) más metadatos de auditoría:

    - `motor_usado`: ``tesseract_baseline`` | ``docling`` | ``easyocr_raster``
    - `tiempo_pagina_s`: float
    - `gating_tuvo_fallback`: bool
    - `gating_motivos`: lista de strings (vacía si el baseline fue suficiente)
    - `intentos`: lista de {motor, len_texto, tiempo_s, score} por página

    Parameters
    ----------
    pdf_path
        Ruta al PDF multipágina.
    config
        Umbrales; por defecto ``AdaptiveOcrConfig()``.
    log_file / metrics_file
        Si ``write_logs`` es True, se escriben líneas de texto y JSONL.
    write_logs
        Si False, no toca disco (solo retorna dicts).
    """
    cfg = config or AdaptiveOcrConfig()
    log_path = log_file if log_file is not None else _DEFAULT_LOG_FILE
    met_path = metrics_file if metrics_file is not None else _DEFAULT_METRICS_FILE

    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.is_file():
        return [
            {
                "pagina": 0,
                "status": f"error_apertura:no_existe:{pdf_path}",
                "texto": "",
                "motor_usado": "",
                "tiempo_pagina_s": 0.0,
                "gating_tuvo_fallback": False,
                "gating_motivos": [],
                "intentos": [],
            }
        ]

    import fitz

    engines = _RuntimeEngines()

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        return [
            {
                "pagina": 0,
                "status": f"error_apertura:{exc!s}",
                "texto": "",
                "motor_usado": "",
                "tiempo_pagina_s": 0.0,
                "gating_tuvo_fallback": False,
                "gating_motivos": [],
                "intentos": [],
            }
        ]

    n_pages = len(doc)
    doc.close()

    out: list[dict[str, Any]] = []
    tmpdir = tempfile.mkdtemp(prefix="ocr_adaptive_", dir=str(_DEFAULT_LOG_DIR.parent))

    try:
        for page_1based in range(1, n_pages + 1):
            one_pdf = Path(tmpdir) / f"p{page_1based}.pdf"
            _single_page_pdf(pdf_path, page_1based, one_pdf)

            intentos: list[dict[str, Any]] = []
            t0 = time.perf_counter()
            text_t, st_t = _text_baseline_one_page(one_pdf)
            dt_t = time.perf_counter() - t0
            sc_t = quality_score(text_t)
            intentos.append(
                {
                    "motor": "tesseract_baseline",
                    "len_texto": len(text_t),
                    "tiempo_s": round(dt_t, 4),
                    "score": round(sc_t, 2),
                    "status": st_t,
                }
            )

            motives = gating_motives(text_t, cfg)
            use_fallback = needs_fallback(text_t, cfg)

            chosen_text = text_t
            chosen_motor = "tesseract_baseline"
            chosen_status = st_t
            had_fallback = False

            if use_fallback and (cfg.enable_docling or cfg.enable_easyocr):
                had_fallback = True
                best_score = sc_t
                best_text = text_t
                best_motor = "tesseract_baseline"
                best_status = st_t

                if cfg.enable_docling:
                    try:
                        if engines.docling_converter is None:
                            engines.docling_converter = _get_docling_converter(cfg)
                        t1 = time.perf_counter()
                        text_d = _text_docling(engines.docling_converter, one_pdf)
                        dt_d = time.perf_counter() - t1
                        sc_d = quality_score(text_d)
                        intentos.append(
                            {
                                "motor": "docling",
                                "len_texto": len(text_d),
                                "tiempo_s": round(dt_d, 4),
                                "score": round(sc_d, 2),
                                "status": "docling_md",
                            }
                        )
                        if sc_d > best_score:
                            best_score, best_text, best_motor = sc_d, text_d, "docling"
                            best_status = "adaptive_docling"
                    except Exception as exc:
                        intentos.append(
                            {
                                "motor": "docling",
                                "error": str(exc),
                                "tiempo_s": None,
                                "score": None,
                            }
                        )

                # EasyOCR solo si sigue haciendo falta o mejora el mejor candidato
                still_bad = needs_fallback(best_text, cfg)
                if cfg.enable_easyocr and (still_bad or best_motor == "tesseract_baseline"):
                    try:
                        if engines.easyocr_reader is None:
                            engines.easyocr_reader = _get_easyocr_reader(cfg)
                        t2 = time.perf_counter()
                        text_e = _text_easyocr(
                            engines.easyocr_reader,
                            pdf_path,
                            page_1based,
                            cfg.easyocr_dpi,
                        )
                        dt_e = time.perf_counter() - t2
                        sc_e = quality_score(text_e)
                        intentos.append(
                            {
                                "motor": "easyocr_raster",
                                "len_texto": len(text_e),
                                "tiempo_s": round(dt_e, 4),
                                "score": round(sc_e, 2),
                                "status": "easyocr",
                            }
                        )
                        if sc_e > best_score:
                            best_score = sc_e
                            best_text = text_e
                            best_motor = "easyocr_raster"
                            best_status = "adaptive_easyocr"
                    except Exception as exc:
                        intentos.append(
                            {
                                "motor": "easyocr_raster",
                                "error": str(exc),
                                "tiempo_s": None,
                                "score": None,
                            }
                        )

                chosen_text = best_text
                chosen_motor = best_motor
                chosen_status = best_status

            total_time = sum(
                x.get("tiempo_s") or 0.0
                for x in intentos
                if isinstance(x.get("tiempo_s"), (int, float))
            )

            row: dict[str, Any] = {
                "pagina": page_1based,
                "status": chosen_status,
                "texto": chosen_text,
                "motor_usado": chosen_motor,
                "tiempo_pagina_s": round(total_time, 4),
                "gating_tuvo_fallback": had_fallback,
                "gating_motivos": motives if use_fallback else [],
                "intentos": intentos,
            }
            out.append(row)

            if write_logs:
                fb = "OK"
                if had_fallback:
                    fb = f"FALLBACK→{chosen_motor}"
                line = (
                    f"{_ts_iso()} [PAGE {page_1based}/{n_pages}] {fb} | "
                    f"motor_final={chosen_motor} | len={len(chosen_text)} | "
                    f"t={row['tiempo_pagina_s']}s | baseline_motivos={motives or '-'}"
                )
                _append_log_line(log_path, line)
                _append_metrics_jsonl(
                    met_path,
                    {
                        "ts": _ts_iso(),
                        "pdf": str(pdf_path),
                        "pagina": page_1based,
                        "motor_usado": chosen_motor,
                        "len_texto": len(chosen_text),
                        "tiempo_pagina_s": row["tiempo_pagina_s"],
                        "gating_tuvo_fallback": had_fallback,
                        "gating_motivos": motives,
                    },
                )

    finally:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)

    return out


def process_pdf_adaptive_light(
    pdf_path: Path | str,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """
    Igual que ``process_pdf_adaptive`` pero cada dict solo expone las claves
    de ``process_pdf`` (``pagina``, ``status``, ``texto``) para callers que
    no quieren metadatos extra.
    """
    raw = process_pdf_adaptive(pdf_path, **kwargs)
    return [
        {"pagina": r["pagina"], "status": r["status"], "texto": r["texto"]} for r in raw
    ]


if __name__ == "__main__":
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="OCR adaptativo (gating + fallback)")
    ap.add_argument("pdf", type=Path, help="Ruta al PDF")
    ap.add_argument("--min-len", type=int, default=500)
    ap.add_argument("--min-fields", type=int, default=2)
    ap.add_argument("--max-garbage", type=float, default=0.12)
    ap.add_argument("--no-log", action="store_true", help="No escribir logs en disco")
    args = ap.parse_args()

    cfg = AdaptiveOcrConfig(
        min_text_len=args.min_len,
        min_nonnull_fields=args.min_fields,
        max_garbage_ratio=args.max_garbage,
    )
    res = process_pdf_adaptive(args.pdf, config=cfg, write_logs=not args.no_log)
    for r in res:
        print(
            f"p{r['pagina']} motor={r['motor_usado']} status={r['status']} "
            f"len={len(r['texto'])} t={r['tiempo_pagina_s']}s fallback={r['gating_tuvo_fallback']}"
        )
