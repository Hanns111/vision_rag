# Checklist — poblar el piloto (orden fijo)

Objetivo: **15 páginas** en el piloto = **15 archivos JSON** en `labels/` (además de `_PLANTILLA_pagina.json`, que no cuenta). Misma norma que `docs/ROADMAP_PROYECTO.md` §4.1.

---

## Qué significa “15 páginas”

- Es **15 hojas PDF** concretas (la 3ª hoja de un archivo cuenta como **una** página).
- Cada una tendrá **un** archivo `labels/{doc_id}_p{page_index}.json`.
- **No** son 15 PDFs obligatoriamente: puede ser 1 PDF de 15 páginas, o 3 PDFs que sumen 15 páginas elegidas, etc.

---

## `raw/` — qué PDFs y cómo nombrarlos

| Qué poner | Facturas, boletas, notas de crédito/débito, recibos por honorarios u otros **comprobantes de pago** peruanos donde tenga sentido rellenar RUC, montos, fecha (esquema `piloto_ocr.v1`). Escaneado o texto digital. |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Cómo nombrar | Un archivo = **`data/piloto_ocr/raw/{doc_id}.pdf`**. El `doc_id` es el nombre **sin** `.pdf`, solo letras/números/guiones (ASCII). Ej.: `raw/fac-001.pdf` → `doc_id` = `fac-001`. |
| Cuántos archivos | Los que necesites para cubrir las **15 páginas** que elegiste (puede ser 1 solo PDF o varios). |

---

## `MANIFEST_PILOTO.csv` — cómo llenarlo

- **Una fila por cada PDF** que pusiste en `raw/`.
- Columnas (cabecera ya está en el archivo):
  - **`doc_id`**: igual al nombre del `.pdf` sin extensión.
  - **`archivo_raw_relativo`**: desde `data/piloto_ocr/`, ej. `raw/fac-001.pdf`.
  - **`paginas_en_pdf`**: total de hojas del PDF (lo ves en el lector PDF).
  - **`paginas_en_piloto`**: cuántas de esas hojas **entran** en el piloto (≤ total).
  - **`indices_paginas_en_pdf`**: números de hoja **desde 1** (primera hoja = 1), separados por comas, **sin espacios** tras la coma recomendado: `1,2,3` o `"1,2,3"` si tu Excel rompe el CSV. Debe haber tantos números como `paginas_en_piloto`.
  - **`notas`**: opcional.
- **Regla:** suma de **`paginas_en_piloto`** de todas las filas = **15**.
- Guarda el archivo como **CSV UTF-8** (si usas Excel, exportar CSV UTF-8 para no romper tildes en `notas`).

---

## `labels/` — los 15 JSON con la plantilla

1. Abre `labels/_PLANTILLA_pagina.json` (no lo borres; es plantilla).
2. Por **cada** página incluida en el manifiesto:
   - Crea un archivo nuevo: **`{doc_id}_p{page_index}.json`**  
     Ej.: página 7 del PDF `fac-001.pdf` → `fac-001_p7.json`.
   - Copia el **contenido** de la plantilla en ese archivo nuevo (o “Guardar como…” con el nombre correcto).
   - Edita: `doc_id`, `page_index`, `etiquetado_por`, `fecha_etiquetado`, todos los `campos`, `notas`.
   - Deja **`schema_version": "piloto_ocr.v1"`** sin cambiar.
3. Al terminar, debes tener **exactamente 15** archivos que sigan el patrón `algo_pN.json` **excluyendo** solo `_PLANTILLA_pagina.json`.

---

## `metrics/` — qué hacer antes del baseline

- **Antes** de la primera corrida de `document_ocr_runner.py`: no tienes que crear nada obligatorio aquí; basta `METRICAS_MINIMAS.md`.
- **Después** del baseline: guarda aquí `baseline_paso1_YYYYMMDD.csv` y, si quieres, `run_log_YYYYMMDD.txt` (ver `METRICAS_MINIMAS.md`).

---

## Pasos en orden (hazlos así)

1. Elige tus PDFs de comprobantes (no subvención).
2. Asigna un **`doc_id`** distinto a cada PDF.
3. Copia cada uno a `data/piloto_ocr/raw/{doc_id}.pdf`.
4. Cuenta páginas por PDF y decide qué **15 hojas** entran en total.
5. Rellena **`MANIFEST_PILOTO.csv`** (suma 15 en `paginas_en_piloto`).
6. Genera los **15 JSON** en `labels/` con nombres `{doc_id}_p{page_index}.json` alineados al manifiesto.
7. Comprueba: 15 JSON + plantilla en `labels/`; PDFs en `raw/`; manifiesto coherente.
8. **Entonces** puedes apuntar `scripts/document_ocr_runner.py` a `data/piloto_ocr/raw` y ejecutar PASO 1 (ver `PILOTO_OPERATIVO.md` §5).

---

## Listo para PASO 1 baseline medible cuando

- [ ] Están los PDFs en `raw/` con nombres `{doc_id}.pdf`.
- [ ] `MANIFEST_PILOTO.csv` suma **15** en `paginas_en_piloto` y los índices coinciden con hojas reales.
- [ ] Hay **15** archivos de etiqueta (sin contar `_PLANTILLA_pagina.json`) y cada uno tiene gold razonable para comparar con el OCR en métricas.

Si falta gold en algún campo, puedes usar `null` según §4.1 del roadmap; las métricas por campo ignoran o penalizan según definición allí.
