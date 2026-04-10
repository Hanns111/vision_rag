# Informe PASO 1 — Baseline OCR (piloto DEBEDSAR)

**Fecha corrida:** 2026-04-10  
**Commit piloto PASO 0:** `54517f7` (15/15 páginas etiquetadas)  
**Script:** `scripts/document_ocr_runner.py` (sin cambios de lógica OCR; solo ruta por defecto a `data/piloto_ocr/raw/`).

---

## 1. Cómo se corrió

Desde la raíz del repositorio `vision_rag`:

1. Dependencias: `pip install -r scripts/requirements-ocr.txt` (PyMuPDF, OpenCV, pytesseract, numpy).  
2. Tesseract OCR instalado en el sistema (Windows), idioma `spa+eng` para páginas sin capa de texto suficiente.  
3. Comando ejecutado:

```text
python scripts/document_ocr_runner.py
```

El `__main__` recorre **todos** los `.pdf` en `data/piloto_ocr/raw/` en orden alfabético: `rend-debedsar-amiquero-2026.pdf`, `ri-debedsar-amiquero-2026.pdf`, `sol-viat-debedsar-2026.pdf`.

Salida completa de consola guardada en: **`run_log_20260410.txt`** (incluye `elapsed_seconds` al final de la corrida; ~14–17 s en el entorno de ejecución).

---

## 2. Archivos procesados

| Archivo | Páginas totales PDF | En piloto (manifiesto) |
|---------|---------------------|-------------------------|
| `raw/rend-debedsar-amiquero-2026.pdf` | 31 | 12 índices |
| `raw/ri-debedsar-amiquero-2026.pdf` | 1 | 1 |
| `raw/sol-viat-debedsar-2026.pdf` | 7 | 2 |

El script procesó **cada página** de cada PDF (no solo las 15 del piloto). Las métricas tabuladas en **`baseline_paso1_20260410.csv`** se limitan a las **15** filas `(doc_id, page_index)` del `MANIFEST_PILOTO.csv`.

---

## 3. Resultados producidos

| Archivo | Descripción |
|---------|-------------|
| `metrics/run_log_20260410.txt` | Volcado de la corrida: por PDF y por página, `status` y texto extraído (dict impreso). |
| `metrics/baseline_paso1_20260410.csv` | 15 filas piloto: `status_capa` (`digital_text` si capa PyMuPDF ≥ 40 caracteres; `ocr` / `ocr_vacio` / otros si aplica), `len_texto`, muestra 200 caracteres. |
| `metrics/INFORME_PASO1_20260410.md` | Este informe. |

**Columna `motor` en el CSV:** valor uniforme `tesseract_baseline` como etiqueta de **corrida baseline**; en realidad las páginas con `digital_text` usaron **solo capa digital (PyMuPDF)**. El script híbrido aplica Tesseract solo si la capa es insuficiente.

---

## 4. Coherencia previa (verificación)

- **MANIFEST + raw + labels:** 15/15 coherentes; sin cambios de selección.  
- **Páginas p7 y p8** (informe/anexo, `requiere_revision: true` en gold): **se mantienen** en el piloto; no se detectó incoherencia grave que obligue a excluirlas del baseline.

---

## 5. Limitaciones y fallos observados

- **Exactitud por campo (§4.3 roadmap):** no calculada en este PASO 1: haría falta **parsing** de RUC, montos, etc. desde el texto bruto → corresponde a fases posteriores (p. ej. PASO 4), no al runner actual.  
- **Rendición págs. 1–4 y otras:** muchas salieron como **`ocr`** (escaneo o poca capa); texto con **artefactos** y tablas difíciles (p. ej. cuadros de gasto en anexo 3).  
- **`sol-viat-debedsar-2026` pág. 6:** en el PDF completo apareció **`ocr_vacio`** (no está en las 15 del piloto).  
- **Codificación:** consola Windows puede mostrar caracteres sustituidos; el CSV y este informe están en UTF-8.  
- **Comparación con otros motores (Paddle, Docling, etc.):** no realizada (fuera de alcance PASO 1).

---

## 6. Estado PASO 1

**Ejecutado:** sí — baseline corrido sobre los PDF del piloto; artefactos generados bajo `data/piloto_ocr/metrics/`.

