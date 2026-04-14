# Piloto OCR — Instrucciones operativas (PASO 0 → PASO 1)

Documento **operativo**; no sustituye `docs/ROADMAP_PROYECTO.md` §4.1 (solo lo ejecuta).

**Checklist paso a paso (lo que debes hacer tú):** **[`CHECKLIST_POBLADO.md`](CHECKLIST_POBLADO.md)**.

---

## 1. Qué poner en `raw/`

**Contenido:** PDFs de **comprobantes de pago** peruanos (factura, boleta, nota de crédito, recibo honorarios, etc.) donde el **objetivo** del piloto sea extraer los campos del esquema `piloto_ocr.v1` (RUC, montos, fechas, etc.). Pueden ser escaneados o con capa de texto.

**No subvención:** no uses expedientes FONDEP ni carpetas de `control_previo/` para este piloto.

**Cantidad:** exactamente **15 páginas** cuentan en el piloto (suma de las filas `paginas_en_piloto` del manifiesto = 15).

---

## 2. Convención de nombres (obligatoria)

| Elemento | Regla |
|----------|--------|
| **`doc_id`** | Solo ASCII: `a-z`, `A-Z`, `0-9`, guiones `-`. Sin espacios ni tildes. Ej.: `fac-2025-001`, `rec-001`. Debe ser **único** en el piloto. |
| **Archivo en `raw/`** | **`{doc_id}.pdf`** — el nombre del archivo **sin extensión** es exactamente el `doc_id`. Ej.: `doc_id` = `fac-2025-001` → archivo `raw/fac-2025-001.pdf`. |
| **Un PDF puede aportar varias páginas al piloto** | Un solo `doc_id` = un solo archivo; las páginas se numeran `page_index` 1, 2, … **N** según el orden del PDF (primera hoja = 1). |

Si un mismo PDF tiene 10 páginas en el piloto, hay **10** archivos JSON: `{doc_id}_p1.json` … `{doc_id}_p10.json`.

---

## 3. `MANIFEST_PILOTO.csv`

Columnas (una fila por **archivo PDF**):

| Columna | Significado |
|---------|-------------|
| `doc_id` | Igual que el nombre del archivo sin `.pdf`. |
| `archivo_raw_relativo` | Ruta desde `data/piloto_ocr/`, ej. `raw/fac-2025-001.pdf`. |
| `paginas_en_pdf` | Total de páginas del archivo (según visor PDF). |
| `paginas_en_piloto` | Cuántas de esas páginas entran en el piloto (≤ `paginas_en_pdf`). |
| `indices_paginas_en_pdf` | Páginas **1-based** de este PDF que **sí** se etiquetan, separadas por comas **sin espacios** (`1,2,3`). Si Excel altera el CSV, entrecomillar el campo o guardar CSV UTF-8 desde editor. Debe haber **exactamente** `paginas_en_piloto` índices. |
| `notas` | Libre (origen, tipo de doc, etc.). |

**Regla de suma:** la suma de `paginas_en_piloto` de **todas** las filas debe ser **15**.

**Coherencia:** por cada índice `k` listado en `indices_paginas_en_pdf` debe existir `labels/{doc_id}_pk.json` (ej. `p3` para página 3).

---

## 4. `labels/` — un JSON por página en piloto

- Nombre: **`{doc_id}_p{page_index}.json`** con `page_index` igual a un valor en `indices_paginas_en_pdf` para ese `doc_id`.
- Copiar desde `_PLANTILLA_pagina.json`, cambiar `doc_id`, `page_index`, rellenar `campos` y metadatos.
- **`schema_version`:** siempre `piloto_ocr.v1`.

---

## 5. PASO 1 baseline (`document_ocr_runner.py`) — sin código nuevo

1. Copiar o enlazar los PDFs ya listados en `raw/` (según manifiesto).
2. En el `__main__` del script, **apuntar** la carpeta a `data/piloto_ocr/raw` (o a un directorio que contenga solo esos `.pdf`).
3. Ejecutar: `pip install -r scripts/requirements-ocr.txt` y luego `python scripts/document_ocr_runner.py` (desde `vision_rag` o ajustando rutas).
4. Guardar salida (texto por página) y tiempos en `metrics/` según `METRICAS_MINIMAS.md` y `docs/ROADMAP_PROYECTO.md` §4.3; nombre sugerido: `baseline_paso1_YYYYMMDD.csv` + `run_log_YYYYMMDD.txt`.

**Listo para baseline** cuando: `raw/` tiene los PDFs nombrados, el manifiesto suma 15 y las 15 etiquetas existen (o las etiquetas se completan en paralelo a la primera corrida; para métricas formales hace falta gold).

---

## 6. Ejemplo de manifiesto (ilustrativo)

Sustituir por tus archivos reales; la suma de `paginas_en_piloto` debe ser **15**.

```csv
doc_id,archivo_raw_relativo,paginas_en_pdf,paginas_en_piloto,indices_paginas_en_pdf,notas
fac-lote-a,raw/fac-lote-a.pdf,10,10,"1,2,3,4,5,6,7,8,9,10",ejemplo
fac-lote-b,raw/fac-lote-b.pdf,5,5,"1,2,3,4,5",ejemplo
```

---

## 7. Criterio operativo preferente — entorno de ejecución (OCR avanzado, bake-off PASO 2, GPU)

Esta sección es **criterio de trabajo preferente** para el proyecto (no una nota marginal): define **dónde** debe ejecutarse preferentemente el **OCR avanzado**, el **bake-off PASO 2** y las pruebas con herramientas **sensibles al runtime o a GPU**, para que los resultados sean **reproducibles** y no se confunda fallo de entorno con calidad del motor.

**Propósito:** evitar conclusiones injustas cuando un motor **falla por incompatibilidad de runtime** (drivers, oneDNN, PyTorch/CUDA, etc.) y no por calidad intrínseca del modelo; y evitar que **Windows** actúe como **referencia principal** del bake-off cuando **Linux/Ubuntu vía WSL** (p. ej. con RTX 5090) es el entorno **más estable** o el único donde la herramienta es reproducible.

| Rol | Regla operativa |
|-----|-----------------|
| **Entorno preferente** | **Linux / Ubuntu vía WSL** es el entorno **preferente y de primera opción** para: **OCR avanzado**, **bake-off PASO 2**, y pruebas con motores o dependencias **sensibles al runtime o GPU** (p. ej. PaddleOCR, pilas con CUDA, modelos pesados), cuando en ese entorno la pila es **más estable** o permite **aprovechar la GPU** de forma fiable. |
| **Windows (secundario / auxiliar)** | **Windows** puede usarse como entorno **alterno o auxiliar** (etiquetado, baseline ligero, tareas que no dependan de una pila frágil). **No** debe tratarse como entorno **principal de referencia** para bake-off ni para decisiones finales sobre motores cuando en Windows aparecen **fallos de runtime o incompatibilidades** que **no** se reproducen o se evitan en **Linux/WSL** y **distorsionan** la comparación. |
| **Interpretación de métricas PASO 2** | Los resultados deben **interpretarse siempre según el entorno de ejecución** documentado (OS, CPU/GPU, versiones, en `run_log` o informe). Una tabla de bake-off corrida solo en Windows **no** sustituye por sí sola a una evaluación en el entorno preferente cuando este último está disponible para el tipo de prueba. |
| **Descarte de herramienta** | Una herramienta **no** se da por descartada definitivamente **solo** porque falló en **Windows** si el fallo es **típico de entorno** (DLL, oneDNN, CUDA). La decisión debe apoyarse en **repetición en Linux/WSL** (u otro runtime estable) o en criterio explícito documentado. |
| **Resumen** | Si **Linux/WSL** ofrece mayor estabilidad y uso adecuado de **GPU** para OCR avanzado, las **corridas de comparación seria** (bake-off) deben **priorizar** ese entorno; Windows queda como **secundario** cuando existan limitaciones que afecten la equidad o reproducibilidad de la medición. |

**Subvención:** esta sección no altera normativa de negocio; solo criterio de **ingeniería y medición**.

**Relación:** `docs/DECISIONES_TECNICAS.md` **D-12** · `data/piloto_ocr/metrics/METRICAS_MINIMAS.md` (entorno).
