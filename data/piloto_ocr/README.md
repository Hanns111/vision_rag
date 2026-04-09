# `data/piloto_ocr/` — Piloto PASO 0

## Parámetros fijos (v1)

- **N = 15 páginas** etiquetadas (ver `MANIFEST_PILOTO.csv`).
- **Formato:** `labels/{doc_id}_p{page_index}.json` con **`schema_version: piloto_ocr.v1`**.
- **Plantilla:** `labels/_PLANTILLA_pagina.json` (copiar y renombrar; no commitear datos personales reales si aplica política).

## Árbol

```
piloto_ocr/
  MANIFEST_PILOTO.csv
  README.md
  raw/              # PDFs (contenido *.pdf no va a git por .gitignore global)
  labels/           # 15 JSON + plantilla
  metrics/          # CSV de corridas + METRICAS_MINIMAS.md
```

## Cierre

Checklist en **`docs/ROADMAP_PROYECTO.md` §9**.
