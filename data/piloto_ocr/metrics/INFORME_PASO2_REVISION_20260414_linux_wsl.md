# Informe PASO 2 — Bake-off revisable (2026-04-14)

**Entorno de ejecución:** WSL2 Ubuntu (preferente D-12)

**Etiqueta de corrida (`--tag`):** `linux_wsl` — CSV/XLSX/MD con sufijo `_linux_wsl`. Textos por motor: `data/piloto_ocr/metrics/paso2_linux_wsl/<motor>/`.

Generado: 2026-04-14 00:32:32 -0500

## Comparación preferente (D-12)

Esta corrida en **Linux/Ubuntu vía WSL** se trata como la **comparación preferente y más confiable** frente a la corrida previa en **Windows** (artefactos `bakeoff_paso2_*_20260413.*` / `INFORME_PASO2_REVISION_20260413.md` sin sufijo `linux_wsl`), cuando Windows pudo introducir limitaciones de runtime (p. ej. PaddleOCR / oneDNN).

### Referencia Windows (2026-04-13)

| motor | P macro | R macro | F1 macro | s/página | % págs. fallo |
|-------|---------|---------|----------|----------|----------------|
| tesseract_baseline | 0.9833 | 0.6572 | 0.7388 | 0.0096 | 100.0 |
| docling | 0.9833 | 0.5761 | 0.6852 | 1.5756 | 100.0 |
| paddleocr | 0.0 | 0.0 | 0.0 | 0.0 | 100.0 |

*Valores tomados del informe Windows `INFORME_PASO2_REVISION_20260413.md` (Paddle no ejecutó inferencia en ese entorno).*

## Motores

- **tesseract_baseline**: ejecutado.
- **docling (CPU)**: ejecutado.
- **paddleocr**: ejecutado

## Esta corrida (WSL/Linux)

### Tabla comparativa (resumen)

| motor | P macro* | R macro* | F1 macro* | s/página | % págs. fallo |
|-------|----------|----------|-----------|----------|----------------|
| tesseract_baseline | 0.9833 | 0.6572 | 0.7388 | 0.0249 | 100.0 |
| docling | 0.9833 | 0.5761 | 0.6852 | 3.1312 | 100.0 |
| paddleocr | 0.9733 | 0.5422 | 0.6194 | 2.2201 | 100.0 |

*Media aritmética de precision/recall/F1 **por campo** (10 campos del extractor mínimo).

## Windows vs WSL/Linux

| Aspecto | Windows (corrida ref. 2026-04-13) | WSL/Linux (esta corrida) |
|---------|-----------------------------------|---------------------------|
| Artefactos | `bakeoff_paso2_*_20260413.*`, `paso2/<motor>/` | mismos nombres con sufijo `_linux_wsl` y carpeta `paso2_linux_wsl/` |
| Confianza D-12 | secundaria si el runtime distorsionó OCR | **preferente** para decisión de motores |
| PaddleOCR | no inferencia (0 métricas útiles) | PaddleOCR **sí** ejecutó inferencia en WSL (hoja Excel `paddleocr`, textos `data/piloto_ocr/metrics/paso2_linux_wsl/paddleocr/`). |

## Archivos

- Excel: `data/piloto_ocr/metrics/bakeoff_paso2_revision_20260414_linux_wsl.xlsx`
- CSV consolidado: `data/piloto_ocr/metrics/bakeoff_paso2_consolidado_20260414_linux_wsl.csv`
- Textos por motor: `data/piloto_ocr/metrics/paso2_linux_wsl/<motor>/`

## Recomendación preliminar actualizada

Comparar la tabla **Esta corrida (WSL/Linux)** con **Referencia Windows**. Priorizar F1 macro y recall por campo según ROADMAP; si PaddleOCR solo es viable en WSL, la recomendación de motor puede cambiar respecto de Windows.
