# `data/piloto_ocr/` — Piloto PASO 0

## Parámetros fijos (v1)

- **N = 15 páginas** etiquetadas (ver `MANIFEST_PILOTO.csv`).
- **Formato:** `labels/{doc_id}_p{page_index}.json` con **`schema_version: piloto_ocr.v1`**.
- **Plantilla:** `labels/_PLANTILLA_pagina.json` (copiar y renombrar; no commitear datos personales reales si aplica política).

## Instrucciones para poblar `raw/` y alinear manifiesto + labels

1. **[`CHECKLIST_POBLADO.md`](CHECKLIST_POBLADO.md)** — pasos numerados y checklist.  
2. **[`PILOTO_OPERATIVO.md`](PILOTO_OPERATIVO.md)** — reglas y PASO 1 baseline.

## Árbol

```
piloto_ocr/
  PILOTO_OPERATIVO.md
  MANIFEST_PILOTO.csv
  README.md
  raw/              # PDFs: {doc_id}.pdf (no van a git)
  labels/           # 15 JSON + plantilla
  metrics/          # CSV de corridas + METRICAS_MINIMAS.md
```

## Cierre

Checklist en **`docs/ROADMAP_PROYECTO.md` §9**.
