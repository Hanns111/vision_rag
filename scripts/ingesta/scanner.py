"""
Ingesta: detecta PDFs de un expediente, copia a `procesados/{id}/source/`
y emite `metadata.json` con hashes SHA-1 para idempotencia y trazabilidad.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DocumentoIngresado:
    nombre: str
    ruta_origen: str
    ruta_destino: str
    sha1: str
    tamano_bytes: int
    paginas: int | None


@dataclass
class ExpedienteIngresado:
    expediente_id: str
    ruta_origen: str
    ruta_destino: str
    fecha_ingesta: str
    documentos: list[DocumentoIngresado]


def _sha1_of(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _count_pages(pdf_path: Path) -> int | None:
    try:
        import fitz
    except ImportError:
        return None
    try:
        doc = fitz.open(str(pdf_path))
        n = len(doc)
        doc.close()
        return n
    except Exception:
        return None


def _ts_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def _append_trace(trace_path: Path, msg: str) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with open(trace_path, "a", encoding="utf-8") as f:
        f.write(f"{_ts_iso()} {msg}\n")


def ingest_expediente(
    src_dir: Path | str,
    dest_root: Path | str,
    expediente_id: str | None = None,
) -> ExpedienteIngresado:
    """
    Copia los PDFs de `src_dir` a `{dest_root}/{expediente_id}/source/` y
    escribe `metadata.json` con hashes. No mueve ni borra el original.

    `expediente_id` por defecto: nombre de `src_dir`.
    """
    src = Path(src_dir).resolve()
    if not src.is_dir():
        raise FileNotFoundError(f"no es carpeta: {src}")

    exp_id = expediente_id or src.name
    dest = Path(dest_root).resolve() / exp_id
    source_dir = dest / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    (dest / "ocr_cache").mkdir(exist_ok=True)
    (dest / "extractions").mkdir(exist_ok=True)

    trace = dest / "_trace.log"
    _append_trace(trace, f"INGESTA inicio src={src} dest={dest}")

    docs: list[DocumentoIngresado] = []
    for pdf in sorted(src.glob("*.pdf")):
        digest = _sha1_of(pdf)
        target = source_dir / pdf.name
        if not target.exists() or _sha1_of(target) != digest:
            shutil.copy2(pdf, target)
            _append_trace(trace, f"COPY {pdf.name} sha1={digest}")
        else:
            _append_trace(trace, f"SKIP_COPY {pdf.name} ya_presente sha1={digest}")
        docs.append(
            DocumentoIngresado(
                nombre=pdf.name,
                ruta_origen=str(pdf),
                ruta_destino=str(target),
                sha1=digest,
                tamano_bytes=pdf.stat().st_size,
                paginas=_count_pages(target),
            )
        )

    res = ExpedienteIngresado(
        expediente_id=exp_id,
        ruta_origen=str(src),
        ruta_destino=str(dest),
        fecha_ingesta=_ts_iso(),
        documentos=docs,
    )

    with open(dest / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(asdict(res), f, ensure_ascii=False, indent=2)

    _append_trace(trace, f"INGESTA fin documentos={len(docs)}")
    return res
