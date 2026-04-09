"""Genera MANIFEST_INGESTION.csv por carpeta bajo control_previo/NN_* y un CSV maestro."""
from __future__ import annotations

import csv
import os
from pathlib import Path


def priority_and_role(cat_name: str, rel: str) -> tuple[str, str, str]:
    r = rel.replace("\\", "/").upper()
    if "EXPEDIENTES_REVISION" in r:
        return "alta", "evidencia_expediente", "Revision de caso; OCR si escaneado."
    if "ANTIGUA_DIRECT" in r or "HASTA_05_02_2026" in r:
        return "baja", "normativa_historica", "Solo hechos bajo directiva antigua."
    if "NUEVA_DIRECTIVA" in r or "DI-003-01" in r or "RSG_023" in r:
        return "alta", "normativa_vigente", "Paquete viaticos vigente feb.2026."
    if "PAUTAS" in r and "REMISION" in r:
        return "alta", "pautas_marco", "Marco remision expedientes pago."
    if "CONCURSO INTEGRIDAD" in r:
        return "baja", "referencia_institucional", "No es norma de pago de expediente."
    if "CAPACITACIONES" in r or r.endswith(".MP4"):
        return "media", "capacitacion", "Video; no ingest texto directo."
    if "DETRACCIONES" in r and "NORMATIVAS DETRACCIONES" in r:
        return "alta", "normativa_tributaria", "Base SUNAT detracciones."
    if "042" in r and "CAJA" in r:
        return "alta", "normativa_vigente", "RJ/directiva caja chica 2026."
    if "ENCARGO" in r and "261" in r:
        return "alta", "normativa_vigente", "Directiva encargos."
    if "PLANTILLA" in r:
        return "media", "plantilla_trabajo", "Apoyo armado expediente."
    if "TASAS DEL IGV" in r:
        return "media", "normativa_complementaria", "Contexto tributario."
    return "media", "normativa_o_anexo", "Revisar manualmente para ingest RAG."


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    base = repo / "control_previo"
    if not base.is_dir():
        raise SystemExit(f"No existe {base}")

    cats = sorted(p for p in base.iterdir() if p.is_dir() and p.name[:2].isdigit())
    all_rows: list[dict[str, str]] = []

    for cat in cats:
        rows: list[tuple[str, str, str, str]] = []
        for root, _, files in os.walk(cat):
            for f in files:
                if f.startswith(".") or f == "MANIFEST_INGESTION.csv":
                    continue
                full = Path(root) / f
                rel = full.relative_to(cat).as_posix()
                pr, role, note = priority_and_role(cat.name, rel)
                rows.append((rel, pr, role, note))
        rows.sort(key=lambda x: (x[1] != "alta", x[0]))
        out = cat / "MANIFEST_INGESTION.csv"
        with out.open("w", newline="", encoding="utf-8-sig") as fp:
            w = csv.writer(fp)
            w.writerow(["ruta_relativa", "prioridad_ingest", "rol", "notas"])
            w.writerows(rows)
        for rel, pr, role, note in rows:
            all_rows.append(
                {
                    "categoria": cat.name,
                    "ruta_relativa": rel,
                    "prioridad_ingest": pr,
                    "rol": role,
                    "notas": note,
                }
            )
        print(f"{cat.name}: {len(rows)} filas -> {out.relative_to(repo)}")

    master = base / "MANIFEST_INGESTION_TODO.csv"
    all_rows.sort(
        key=lambda x: (x["categoria"], x["prioridad_ingest"] != "alta", x["ruta_relativa"])
    )
    with master.open("w", newline="", encoding="utf-8-sig") as fp:
        fieldnames = ["categoria", "ruta_relativa", "prioridad_ingest", "rol", "notas"]
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"Maestro: {len(all_rows)} filas -> {master.relative_to(repo)}")


if __name__ == "__main__":
    main()
