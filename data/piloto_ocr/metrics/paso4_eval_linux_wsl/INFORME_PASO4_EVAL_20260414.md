# PASO 4 — Evaluación vs extractor mínimo (2026-04-14)

Generado: 2026-04-14 01:48:15 -0500

OCR fuente: `data/piloto_ocr/metrics/paso2_linux_wsl/tesseract_baseline/*.txt`

## Resumen por campo

| campo | evaluables | ok minimal | ok PASO4 | mejora |
|-------|------------|------------|----------|--------|
| ruc_emisor | 13 | 10 | 10 | +0 |
| tipo_documento | 15 | 11 | 15 | +4 |
| serie_numero | 13 | 5 | 13 | +8 |
| fecha_emision | 14 | 13 | 14 | +1 |
| moneda | 13 | 12 | 12 | +0 |
| monto_subtotal | 9 | 4 | 5 | +1 |
| monto_igv | 9 | 8 | 9 | +1 |
| monto_total | 12 | 6 | 12 | +6 |
| ruc_receptor | 9 | 9 | 9 | +0 |
| razon_social_emisor | 10 | 0 | 0 | +0 |

- **Mejoras netas (suma de deltas por campo):** 21
- **Regresiones (fallos nuevos vs minimal):** 0

## Archivos

- Detalle CSV: `data\piloto_ocr\metrics\paso4_eval_linux_wsl\paso4_eval_detalle_20260414.csv`
- Trazas JSON: `data\piloto_ocr\metrics\paso4_eval_linux_wsl\paso4_eval_trazas_20260414.json`
