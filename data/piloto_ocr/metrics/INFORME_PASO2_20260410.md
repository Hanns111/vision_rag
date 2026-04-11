# Informe PASO 2 — Bake-off OCR/parsing (piloto 15 páginas)

**Fecha:** 2026-04-10  
**Base:** PASO 0 cerrado, PASO 1 en commit `3f2a5cc`.  
**Alcance:** PASO 2 únicamente; sin integración al agente, sin PASO 3, sin subvención.

---

## 1. Herramientas comparadas

| Motor | Descripción |
|--------|-------------|
| **tesseract_baseline** | `scripts/document_ocr_runner.py` — PyMuPDF (capa digital) + Tesseract si hace falta; mismas reglas que PASO 1. |
| **docling** | `DocumentConverter` con **CPU** (`AcceleratorDevice.CPU`); salida Markdown por página (PDF de una página). |
| **easyocr_raster** | Página rasterizada a **300 DPI** + EasyOCR (`es`+`en`, `gpu=False`). Incluido como **motor neuronal alternativo** en este entorno. |
| **PaddleOCR** | **No ejecutado aquí.** Con PaddleOCR 3.x + PaddlePaddle en Windows, la inferencia falló (`NotImplementedError` en ruta oneDNN). Requiere entorno compatible (p. ej. Linux, o downgrade controlado Paddle 2.x / ajuste de runtime) para repetir el bake-off con el candidato D-05. |

Evaluación por campo: **`scripts/piloto_field_extract_minimal.py`** — heurísticas **compartidas** (regex / palabras clave) sobre el texto de cada motor. No es parsing de producto (PASO 4); sirve para **comparabilidad relativa** entre motores sobre las mismas 15 páginas y el mismo gold (`labels/`).

Métrica agregada en CSV: **tasa de aciertos sobre celdas con `valor_gold` no nulo** (117 celdas de 150 posibles; 33 campos con gold `null` no entran en el denominador). Nombre de columna `macro_f1_campos_eval` por alineación al roadmap; en la práctica es **accuracy por celda** bajo extractor mínimo.

---

## 2. Comando exacto

Desde la raíz del repo, con **Python 3.12** (recomendado; 3.14 puede no tener ruedas para Paddle si se reintenta):

```text
pip install -r scripts/requirements-ocr.txt
pip install -r scripts/requirements-paso2.txt
set PYTHONPATH=scripts
python scripts/bakeoff_paso2.py
```

**Nota:** Docling descarga modelos en primera corrida; EasyOCR descarga pesos la primera vez. Tesseract debe estar instalado en el sistema (como en PASO 1).

---

## 3. Archivos generados (`data/piloto_ocr/metrics/`)

| Archivo | Contenido |
|---------|-----------|
| `bakeoff_paso2_tesseract_baseline_20260410.csv` | Detalle por `doc_id`, `page_index`, `campo`, gold/pred/exactitud, `len_texto_pagina`. |
| `bakeoff_paso2_docling_20260410.csv` | Igual, motor docling. |
| `bakeoff_paso2_easyocr_raster_20260410.csv` | Igual, motor EasyOCR. |
| `bakeoff_paso2_resumen_20260410.csv` | Una fila por motor: accuracy agregada, tiempos, longitud media de texto. |
| `bakeoff_paso2_run_log_20260410.txt` | Copia breve del resumen. |
| `INFORME_PASO2_20260410.md` | Este informe. |

---

## 4. Métricas comparativas (resumen)

| Motor | Accuracy celdas (117) | Tiempo total (s) | s/página | len texto medio |
|-------|------------------------|------------------|----------|-----------------|
| tesseract_baseline | **0.6667** (78/117) | **0.17** | **0.012** | 1235 |
| docling | 0.5897 (69/117) | 31.78 | 2.119 | 1965 |
| easyocr_raster | 0.5641 (66/117) | 226.92 | 15.128 | 1226 |

---

## 5. Limitaciones

- Extractor mínimo **no** refleja el techo de ningún motor; mejora fuerte esperada en **PASO 4** (reglas).
- Docling produce más texto (tablas/markdown), no siempre alineado con heurísticas de factura simple.
- **PaddleOCR** pendiente de reproducir en otro entorno para cerrar D-05 contra el mismo script.

---

## 6. Recomendación preliminar (D-05)

Para seguir en el piloto con **coste/latencia razonables** y **mejor puntuación bajo el extractor mínimo actual**, conviene **mantener `tesseract_baseline` (`document_ocr_runner.py`) como motor por defecto** hasta contar con parsing de PASO 4 y, si aplica, repetir el bake-off incluyendo **PaddleOCR** en un runtime soportado. **Docling** puede reservarse para documentos donde importe estructura de tabla/layout y se valide aparte (más lento en CPU en esta corrida).

---

## 7. Estado PASO 2

**Ejecutado:** bake-off documentado con **3 motores** en este repo; **PaddleOCR** registrado como no viable en esta máquina sin trabajo adicional de entorno.

