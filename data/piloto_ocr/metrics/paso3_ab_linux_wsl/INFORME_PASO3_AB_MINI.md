# PASO 3 — Mini A/B (piloto, 2026-04-14)

Generado: 2026-04-14 01:37:48 -0500

## Alcance

- Páginas: `sol-viat-debedsar-2026.pdf` p.2; `rend-debedsar-amiquero-2026.pdf` p.5 y p.19.
- Motor: **tesseract** (`pytesseract`, spa+eng) sobre raster **300 dpi**.
- **A:** gris sin CLAHE (control sin preprocesado adicional).
- **B1:** gris + CLAHE (clipLimit=2.0, tileGridSize=(8, 8)).
- **B2:** B1 + unsharp (sigma=1.0, amount=0.6).

## Regla aplicada

- Éxito: B1 o B2 con **≥ +3** aciertos netos en campos objetivo vs A, y **≤ 1** regresión en campos no objetivo.
- Campos objetivo: `serie_numero`, `monto_subtotal`, `monto_total`, `monto_igv`.

## Decisión final

- **Aciertos campos objetivo (A):** 2
- **B1:** delta neto objetivo vs A = **0**, regresiones no objetivo = **0**
- **B2:** delta neto objetivo vs A = **0**, regresiones no objetivo = **0**

**PASO 3 no justifica más iteración** con esta ronda: el foco debe pasar a **PASO 4** (parsing/heurísticas). Revisar columna `paso4_candidato_A` en el CSV/Excel.

**Evidencia PASO 4:** Algún campo objetivo tiene `paso4_candidato_A=Sí` (valor gold presente en el OCR de A; fallo del extractor mínimo, no de imagen).


## Artefactos

- Rasters: `data\piloto_ocr\metrics\paso3_ab_linux_wsl\rasters`
- OCR txt: `data\piloto_ocr\metrics\paso3_ab_linux_wsl\ocr_txt`
- CSV ancho (delta por campo): `data\piloto_ocr\metrics\paso3_ab_linux_wsl\paso3_ab_delta_por_campo.csv`
- CSV largo (variante): `data\piloto_ocr\metrics\paso3_ab_linux_wsl\paso3_ab_por_variante.csv`
- Excel: `data\piloto_ocr\metrics\paso3_ab_linux_wsl\paso3_ab_revision.xlsx`
