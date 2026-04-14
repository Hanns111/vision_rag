# Informe PASO 2 — Bake-off revisable (2026-04-13)

Generado: 2026-04-13 23:52:08 -0500

## Motores

- **tesseract_baseline**: ejecutado.
- **docling (CPU)**: ejecutado.
- **paddleocr**: no viable / error en este entorno

### PaddleOCR

```
(Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]  (at ..\paddle\fluid\framework\new_executor\instruction\onednn\onednn_instruction.cc:118)

```

## Tabla comparativa (resumen)

| motor | P macro* | R macro* | F1 macro* | s/página | % págs. fallo |
|-------|----------|----------|-----------|----------|----------------|
| tesseract_baseline | 0.9833 | 0.6572 | 0.7388 | 0.0096 | 100.0 |
| docling | 0.9833 | 0.5761 | 0.6852 | 1.5756 | 100.0 |
| paddleocr | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |

*Media aritmética de precision/recall/F1 **por campo** (10 campos del extractor mínimo).

## Archivos

- Excel: `data\piloto_ocr\metrics\bakeoff_paso2_revision_20260413.xlsx`
- CSV consolidado: `data\piloto_ocr\metrics\bakeoff_paso2_consolidado_20260413.csv`
- Textos por motor: `data\piloto_ocr\metrics\paso2/<motor>/`
