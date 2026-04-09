# data/

Datos locales: por defecto **no versionados** salvo lo que indica `.gitignore` (estructura del **piloto OCR** sí).

## Piloto OCR — PASO 0 (`piloto_ocr/`)

| Ruta | Uso |
|------|-----|
| `piloto_ocr/raw/` | PDFs del piloto (**N = 15 páginas** etiquetables en total; ver manifest). |
| `piloto_ocr/labels/` | Ground truth: `schema_version: piloto_ocr.v1`, un JSON por página. |
| `piloto_ocr/metrics/` | CSV PASO 1–2 + `METRICAS_MINIMAS.md`. |
| `piloto_ocr/MANIFEST_PILOTO.csv` | Inventario: qué PDFs y qué páginas cuentan hacia las 15. |
| `piloto_ocr/PILOTO_OPERATIVO.md` | Reglas y PASO 1 baseline. |
| `piloto_ocr/CHECKLIST_POBLADO.md` | **Paso a paso** para poblar raw / manifest / labels. |

**Especificación única:** `docs/ROADMAP_PROYECTO.md` **§4.1–4.3** y **§9** (checklist de cierre).

- No mezclar expedientes de **subvención** aquí hasta cerrar PASO 0 según §9.
- La línea OCR sigue el roadmap **PASO 0 → 7** (`docs/ROADMAP_PROYECTO.md`).
