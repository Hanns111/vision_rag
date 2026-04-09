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
