# vision_rag — Roadmap técnico (PASO 0–7)

> Orden de trabajo y capas **validado**. No sustituye `CURRENT_STATE.md` / `docs/CURRENT_STATE_RAG.md`. **Subvención** y matriz de caso real: **después** de PASO 0–2 cerrados según criterio de este documento.

**Actualizado:** 2026-04-11 · **PASO 0 operativo:** §4.1–4.3 · **Seguimiento:** §9 · **Líneas futuras:** §11

---

## 0. Convención de nombres (oficial)

### 0.1 Regla de oro (texto acordado)

**LLM = último recurso, no primera opción.** El valor está en el **pipeline completo** (datos → OCR/parsing → reglas → validación → RAG), no en sustituir todo por un modelo multimodal.

### 0.2 Números `PASO 0` … `PASO 7`

Solo designan el **orden de ingeniería** del proyecto (medición → extracción → integración). **No** son carpetas de negocio (`control_previo/01_*`); ver §0.4.

| Nombre corto | Significado |
|--------------|-------------|
| **PASO 0** | Ground truth + métricas (piloto fijado en §4.1) |
| **PASO 1** | Baseline (PyMuPDF + `document_ocr_runner.py` / Tesseract) |
| **PASO 2** | Bake-off motores OCR/parsing |
| **PASO 3** | Preprocesado de imagen (dirigido) |
| **PASO 4** | Parsing con reglas + JSON trazable |
| **PASO 5** | Fallback LLM (baja confianza, techo de llamadas) |
| **PASO 6** | RAG normativo + evidencia (`agent_sandbox/`) |
| **PASO 7** | Expediente real + checklist de negocio + matriz |

### 0.3 Pipeline (fases) ↔ PASO

| Fase (idea) | Encaje en PASO |
|-------------|------------------|
| Preprocesamiento | **PASO 3** |
| OCR rápido / batch | **PASO 1–2** |
| Parsing (regex, RUC, montos) | **PASO 4** |
| Fallback LLM | **PASO 5** |
| Validación documental | **PASO 4–7** |
| RAG | **PASO 6** |
| Revisión expediente | **PASO 7** |

### 0.4 Qué **no** son los PASO

Las carpetas **`control_previo/01_viaticos`**, `02_os_oc_pautas`, etc. son **categorías de negocio MINEDU**. **No** se renumeran como PASO 0–7.

---

## 1. Reglas fijas (no reabrir sin datos nuevos)

| # | Regla |
|---|--------|
| R1 | **LLM/VLM no es el motor principal de OCR** en expedientes voluminosos. |
| R2 | **Pipeline híbrido:** preproceso → OCR/parsing auditable → **reglas** → **LLM solo** en baja confianza. |
| R3 | **RAG** (`agent_sandbox/`) = capa **posterior**; no sustituye extracción de facturas escaneadas. |
| R4 | **Medir antes de elegir motor:** ground truth → métricas → baseline → bake-off. |

---

## 2. Estado real del repo (ancla)

| Pieza | Ruta | Notas |
|-------|------|--------|
| RAG + agente | `agent_sandbox/` | `main.py`, `pdf_rag.py`, `orchestrator.py`, `nodes/` |
| Corpus / índice | `agent_sandbox/corpus/`, `agent_sandbox/index/` | |
| OCR baseline | `scripts/document_ocr_runner.py` | PyMuPDF + OpenCV + Tesseract; no integrado al agente |
| Deps OCR | `scripts/requirements-ocr.txt` | + Tesseract en sistema |
| Piloto PASO 0 | `data/piloto_ocr/` | §4.1–4.2 |

**Desalineación:** PASO **6** (RAG) está implementado antes que el pipeline OCR integrado; PASO **0–5** ordenan extracción sin romper el RAG.

---

## 3. Capas

`Capa A — OCR/visión` → `Capa B — parsing + JSON` → `Capa C — validación documental` → `Capa D — corpus normativo` → `Capa E — RAG + evidencia` → `Capa F — revisión expediente`.

---

## 4. PASO 0–7 — Qué hacer y “listo”

| Paso | Entregable | Listo cuando |
|------|------------|--------------|
| **0** | Ground truth + spec métricas | Criterio §4.2 cumplido |
| **1** | Baseline OCR | `metrics/` con corrida comparable a §4.1 |
| **2** | Bake-off | Informe bajo `metrics/` |
| **3–7** | Ver tabla histórica en §4.4 resumen | (sin cambio de criterio) |

### 4.1 PASO 0 — parámetros fijos (v1)

| Parámetro | Valor ejecutable |
|-----------|------------------|
| **N (piloto)** | **15 páginas** etiquetadas. Una **página** = una hoja PDF con al menos un campo del esquema a anotar (si un PDF aporta varias páginas al piloto, se numeran `page_index` 1…N dentro de ese `doc_id`). |
| **Unidad de archivo** | Un JSON por página: `data/piloto_ocr/labels/{doc_id}_p{page_index}.json` |
| **`doc_id`** | Slug ASCII: letras, números, guiones (ej. `fac-2025-001`). |
| **`page_index`** | Entero ≥ 1 (relativo al PDF de ese `doc_id`). |
| **schema_version** | **`piloto_ocr.v1`** (obligatorio en cada JSON). |

**Lista cerrada de campos** (todos bajo `campos`; si no aplica: `null`):

| Clave | Tipo | Regla |
|-------|------|--------|
| `ruc_emisor` | string \| null | 11 dígitos o null |
| `tipo_documento` | string \| null | Código o texto corto (ej. `01`, `03`) |
| `serie_numero` | string \| null | Serie-número unido (ej. `F001-12345`) |
| `fecha_emision` | string \| null | **`YYYY-MM-DD`** |
| `moneda` | string \| null | `PEN`, `USD`, u otro código corto |
| `monto_subtotal` | string \| null | Decimal con punto (ej. `1234.56`) |
| `monto_igv` | string \| null | Mismo formato; null si no figura |
| `monto_total` | string \| null | Mismo formato |
| `ruc_receptor` | string \| null | 11 dígitos o null |
| `razon_social_emisor` | string \| null | Texto libre corto o null |
| `requiere_revision` | boolean | `true` si el etiquetador duda de la lectura |

**Metadatos obligatorios en cada JSON:** `doc_id`, `page_index`, `schema_version`, `etiquetado_por`, `fecha_etiquetado` (ISO date), `campos` (objeto anterior), `notas` (string, puede ser `""`).

**Ejemplo:** ver `data/piloto_ocr/labels/_PLANTILLA_pagina.json`.

### 4.2 Rutas bajo `data/` (inmutables para v1)

| Rol | Ruta |
|-----|------|
| PDFs del piloto | `data/piloto_ocr/raw/` |
| Ground truth | `data/piloto_ocr/labels/` |
| Métricas / manifests | `data/piloto_ocr/metrics/` |
| Inventario del piloto | `data/piloto_ocr/MANIFEST_PILOTO.csv` (una fila por PDF; convención en `data/piloto_ocr/PILOTO_OPERATIVO.md`) |

### 4.3 Métricas mínimas comparables (PASO 1–2)

Definición única para poder comparar motores sobre las **mismas 15 páginas** y los **mismos 11 campos**:

| Métrica | Definición |
|---------|------------|
| **Exactitud por campo** | Para cada campo y cada página: 1 si valor predicho **normalizado** = valor gold **normalizado**; 0 si no. Normalización: trim, mayúsculas en texto; montos: número con tolerancia **±0.01** al valor numérico. |
| **Recall por campo** | Si gold es `null`, no cuenta para recall del campo; si gold no es `null` y pred es `null` o distinto → fallo. |
| **Macro-F1 por campo** | Promedio de F1 del campo sobre las 15 páginas (documentar en CSV bajo `metrics/`). |
| **Tiempo** | `segundos_por_pagina` medido en la corrida (misma máquina al comparar motores). |
| **% páginas con fallo** | Páginas donde existe al menos un campo con exactitud 0. |

Plantilla de nombre de archivo de resultado: `metrics/baseline_paso1_YYYYMMDD.csv`, `metrics/bakeoff_paso2_motor_YYYYMMDD.csv`.

Detalle operativo: `data/piloto_ocr/metrics/METRICAS_MINIMAS.md` · población de `raw/` y baseline: `data/piloto_ocr/PILOTO_OPERATIVO.md`.

### 4.4 Resumen PASO 1–7 (referencia rápida)

| Paso | Entregable | Listo cuando |
|------|------------|--------------|
| **1** Baseline | Corrida `document_ocr_runner.py` sobre `raw/` | CSV en `metrics/` + lista fallos |
| **2** Bake-off | Otro motor vs mismas páginas | CSV comparable + nota breve |
| **3** Preprocesado | Reglas de imagen | AB documentado |
| **4** Parsing reglas | JSON trazable | Métricas en piloto |
| **5** Fallback LLM | Presupuesto llamadas | Log motivación |
| **6** RAG | `agent_sandbox/` | Consultas con fuente |
| **7** Expediente | E2E | Matriz validación |

---

## 5. Después de PASO 0 vs bloqueado hasta cerrarlo

### 5.1 Siguiente acción al cerrar PASO 0 (criterio §4.2)

1. **PASO 1:** ejecutar baseline sobre los PDF en `raw/` que cubran las 15 páginas del `MANIFEST_PILOTO.csv`; guardar salidas y **CSV** de métricas en `metrics/`.
2. Ajustar `document_ocr_runner.py` solo para **rutas de entrada** (sin cambiar lógica OCR obligatoria) si hace falta apuntar a `data/piloto_ocr/raw/`.

### 5.2 Bloqueado hasta que PASO 0 esté cerrado (definición de cierre: §9)

- **PASO 2** formal (bake-off con decisión de motor): no iniciar sin **15** etiquetas en `labels/` + **MANIFEST_PILOTO.csv** completo.
- **Integración** OCR → `orchestrator.py` / agente: sigue **D-07** — bloqueado hasta **PASO 7** por contrato de datos.
- **Reorganización / prompts** de expediente **subvención** y uso productivo de `control_previo/` para pipeline OCR: **después** de PASO 0–1 mínimo (ver §7 del documento histórico).
- **Optimización** de chunking RAG o GraphRAG **por encima** de lo ya hecho: no sustituye medir OCR en facturas; prioridad baja hasta PASO 1–2.

---

## 6. Checklist operativo

1. Completar **§9** (cierre PASO 0).
2. **PASO 1:** `pip install -r scripts/requirements-ocr.txt`; apuntar ejecución a `data/piloto_ocr/raw/`.
3. **PASO 2:** mismas páginas, mismas métricas §4.3.
4. No integrar OCR en `orchestrator.py` hasta **PASO 7**.

---

## 7. Tecnologías (resumen)

PyMuPDF, OpenCV, Tesseract, RAG en `pdf_rag.py`; bake-off: PaddleOCR, Docling, etc. Ver `docs/DECISIONES_TECNICAS.md`.

---

## 8. Documentar después (cuando 0–2 estén cerrados)

1. Categoría **SUBVENCIÓN** (reglas + normativa).
2. Modelo **expediente real** (carpetas, IDs).
3. **Matriz de validación**.

---

## 9. Estado de cierre — PASO 0 (rellenar)

| Criterio | Estado |
|----------|--------|
| `MANIFEST_PILOTO.csv` creado y coherente con `raw/` | ☐ |
| **15** archivos `labels/{doc_id}_p{page_index}.json` con `schema_version: piloto_ocr.v1` | ☐ |
| Ningún PDF del piloto falta por inventariar en manifest | ☐ |
| Lista de páginas = 15 unidades etiquetables | ☐ |

**Fecha de cierre PASO 0:** _______________  

---

## 10. Referencias cruzadas

| Archivo | Uso |
|---------|-----|
| `CURRENT_STATE.md` | RAG + OCR línea + limitaciones |
| `CURSOR_HANDOFF.md` | Mapa repo |
| `data/README.md` | Árbol `data/piloto_ocr/` |
| `data/piloto_ocr/README.md` | Convenciones |
| `data/piloto_ocr/PILOTO_OPERATIVO.md` | Reglas y PASO 1 baseline |
| `data/piloto_ocr/CHECKLIST_POBLADO.md` | Poblar piloto paso a paso |
| `data/piloto_ocr/metrics/METRICAS_MINIMAS.md` | Métricas §4.3 |
| `docs/DECISIONES_TECNICAS.md` | D-01…D-11 |
| `docs/CURRENT_STATE_RAG.md` | Retrieval |

---

## 11. Líneas futuras documentadas (sin número de PASO)

> **Alcance:** registro prudente de direcciones posibles. **No** constituyen el siguiente paso operativo, **no** sustituyen PASO 3–7, **no** reciben numeración de PASO y **no** implican implementación inmediata. **Subvención** y expediente real siguen gobernados por las secciones ya definidas de este documento.

### 11.1 OCR dirigido por regiones (ROI-based extraction)

**Idea (referencia técnica):** detectar regiones relevantes con un modelo tipo **YOLO**, recortar esas regiones y aplicar **OCR o VLM solo sobre esas zonas** (no sobre la página entera por defecto).

**Valor potencial:** puede mejorar precisión y coste cuando el problema deja de ser “qué motor lee la página” y pasa a ser “dónde está cada campo” en layouts densos, siempre que se demuestre con datos.

**Condición para explorarla más adelante:** solo si las **métricas de PASO 2–3** muestran que el cuello de botella está en la **localización de campos dentro de páginas complejas**, y **no** en el motor OCR de página completa. Hasta entonces **no es prioritaria** frente al trabajo acordado del piloto OCR (PASO 2 en curso / cerrado según estado real) y PASO 3.

**Auditoría:** cualquier exploración futura en esta línea debe preservar **trazabilidad por región** (p. ej. bounding box, confianza del detector, texto extraído y relación explícita con el documento fuente), alineado con un sistema **determinista y auditable**.

**Texto de criterio acordado (referencia única):**

Explorar OCR dirigido por regiones (ROI-based extraction) como línea futura solo si las métricas de PASO 2–3 muestran que el cuello de botella está en la localización de campos dentro de páginas complejas, y no en el motor OCR de página completa. Cualquier exploración futura debe preservar trazabilidad por región (bounding box, confianza, texto extraído y relación con el documento fuente).
