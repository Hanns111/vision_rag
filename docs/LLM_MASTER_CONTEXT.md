# LLM_MASTER_CONTEXT — `vision_rag`

> **Propósito:** archivo único de handoff para que cualquier LLM entienda el estado real del proyecto sin ambigüedades.
> **Generado:** 2026-04-22. **Actualizado:** 2026-04-22 (bloque Sandbox auditor v2.1.0 agregado).
> **Último commit registrado al redactar la actualización:** `da06f9b` (`docs: update README with real project state (pipeline active, validation pending)`).
> **Principio rector:** todo lo que afirma este documento está verificado en el repo real. Donde hay duda se marca explícitamente como `⚠ NO CONFIRMADO`.
>
> **Novedad crítica 2026-04-22 (misma sesión):** existe un **sandbox externo al repo** en
> `C:\Users\Hans\Documents\Claude\Projects\INGENIERIA INVERSA_módulo_VIÁTICOS_vision_rag\sandbox_test_cowork_v2\`
> con un motor de **auditoría determinista v2.1.0** (`control_previo_viaticos`) listo para integrar al repo, **pero aún no integrado**. Ver **sección 16** al final de este documento. El repo `vision_rag` no fue tocado.

---

## 0. IDENTIDAD DEL PROYECTO

- **Nombre:** `vision_rag`
- **Repo local:** `C:\Users\Hans\Proyectos\vision_rag`
- **Remoto:** `https://github.com/Hanns111/vision_rag.git`
- **Rama activa:** `main`
- **Objetivo real (no marketing):** sistema de apoyo al **control previo documental** de expedientes administrativos del MINEDU (viáticos, comisiones, rendiciones). Extrae datos tributarios y administrativos de PDFs escaneados/nativos para que un humano pueda validar contra normativa. No reemplaza al revisor.
- **Tipo de sistema:** pipeline OCR determinista (Tesseract) + parsing por reglas (regex + heurísticas) + validación de consistencia contable + RAG normativo separado (línea paralela).
- **Filosofía explícita (del repo, no marketing):**
  - `LLM = último recurso, no primera opción` — regla R1 del roadmap (`docs/ROADMAP_PROYECTO.md §0.1`).
  - `No inventar datos. Si un campo no se puede extraer → null con confianza 0` (AGENT_RULES §3.3).
  - `No forzar resolución en conflicto` — el humano decide.
  - `Excel = artefacto de validación humana, NO fuente técnica` (D-23).
  - `JSON consolidado = fuente de verdad técnica` (D-13).

---

## 1. ESTADO ACTUAL REAL (CRÍTICO)

### Fase vigente

**La fase está ABIERTA.** El pipeline de comprobantes está técnicamente estable y se ha generado el Excel de validación humana, pero **Hans aún no ha realizado la validación manual contra los PDFs originales**. La fase no se cierra hasta que esa revisión se complete con decisión explícita.

**Paralelamente** (no bloqueante para el cierre de esta fase), en la misma sesión de 2026-04-22 se desarrolló un motor externo de auditoría determinista v2.1.0 (`control_previo_viaticos`) **en un sandbox fuera del repo**. Ese paquete NO está integrado a `vision_rag` y su integración también requiere autorización explícita posterior. Ver sección 16.

### Snapshot del pipeline de comprobantes (al 2026-04-22)

- **4 expedientes procesados**: `DEBE2026-INT-0316916`, `DEBEDSAR2026-INT-0103251`, `DIED2026-INT-0250235`, `DIED2026-INT-0344746`.
- **86 comprobantes extraídos**.
- **Estado consistencia**: 15 `OK` (17.4%) · 1 `DIFERENCIA_LEVE` (1.2%) · 15 `DIFERENCIA_CRITICA` (17.4%) · 55 `DATOS_INSUFICIENTES` (64.0%).
- **Requieren revisión manual (flag_revision_manual=SI):** 70 de 86 (81.4%).
- **Excel generado en:** `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (6 hojas, 26 columnas en hoja `comprobantes`).

### Estado del Roadmap PASO 0–7 (fuente: `docs/ROADMAP_PROYECTO.md` §4, §5, §9)

| Paso | Nombre | Estado real |
|---|---|---|
| **PASO 0** | Ground truth + métricas (N=15) | **Parcialmente completado**. 15/15 JSON en `data/piloto_ocr/labels/` con `schema_version=piloto_ocr.v1`; `MANIFEST_PILOTO.csv` completo (3 PDFs: `rend-debedsar-amiquero-2026`, `ri-debedsar-amiquero-2026`, `sol-viat-debedsar-2026`). Checklist §9 con 4 criterios **no tiene fecha de cierre** registrada. Formalmente NO cerrado. |
| **PASO 1** | Baseline OCR | **Ejecutado**. `scripts/document_ocr_runner.py` corrió sobre `raw/`. Artefactos: `baseline_paso1_20260410.csv` + `INFORME_PASO1_20260410.md`. Métricas registradas. |
| **PASO 2** | Bake-off motores OCR | **Ejecutado en dos entornos**. Windows (2026-04-13) y WSL/Linux (2026-04-14). Resultado: Tesseract ganó F1 macro 0.7388 (ambos entornos). Docling 0.6852. PaddleOCR 0.6194 en WSL, 0.0 en Windows (no inferencia). Artefactos: `bakeoff_paso2_*.csv/xlsx/md`. |
| **PASO 3** | Preprocesado de imagen | **Ejecutado parcialmente**. `scripts/paso3_ab_mini.py` existe. Artefactos en `metrics/paso3_ab_linux_wsl/`. ⚠ NO CONFIRMADO si hay cierre formal documentado. |
| **PASO 4** | Parsing con reglas + JSON trazable | **Ejecutado iterativamente**. `scripts/piloto_field_extract_paso4.py` (957 líneas). Evaluaciones en `metrics/paso4_eval_linux_wsl/`. Mejoras posteriores incluyen oráculo SON, cross-check físico 1.5×, validador tributario. |
| **PASO 5** | Fallback LLM (baja confianza) | **No ejecutado**. `agent_sandbox/llm_client.py` existe (333 líneas) pero no está integrado al pipeline de comprobantes. |
| **PASO 6** | RAG normativo + evidencia | **Ejecutado (núcleo funcional)**. `agent_sandbox/pdf_rag.py` (1993 líneas) + `cross_encoder_rerank.py`. Benchmark reciente 12/18 top-1 tras migración a chunking v4 (regresión desde 16/18 previos). |
| **PASO 7** | Expediente real + matriz | **Infra anticipada en uso**. `scripts/ingest_expedientes.py` (780 líneas) ya procesa expedientes reales. Matriz de validación formal **no existe aún**. |

### Bloqueos explícitos (según roadmap §5.2)

- Integración OCR → agente RAG: bloqueado por **D-07** hasta cerrar PASO 7 (contrato de datos).
- PaddleOCR como motor principal: abierto (D-05), dependiente de criterio post-PASO 2.

### Qué funciona REALMENTE (verificado en código + datos)

1. `python scripts/ingest_expedientes.py run-all --src <carpeta> --expediente-id <id>` procesa un expediente end-to-end.
2. OCR por página (Tesseract + CLAHE multi-pasada) sobre PDFs escaneados.
3. Clasificación documental en 9+1 categorías.
4. Extracción determinista de 10 campos (RUC, serie, fecha, montos, razón social).
5. Oráculo SON (letras → número) para `monto_total` (100% en facturas peruanas).
6. Validador tributario por tipo (`GRAVADA / EXONERADA / INAFECTA / MIXTA / NO_DETERMINABLE`).
7. Excel con 6 hojas, priorizado para revisión humana.
8. RAG normativo con recuperación híbrida + cross-encoder opcional.

### Qué es teórico / documentado pero NO implementado

- Módulo completo de **reembolsos por mayor gasto** (solo docs en `docs/modulos/reembolsos/`).
- **ROI-based extraction** (D-11, línea futura documentada en roadmap §11.1).
- **PaddleOCR** como motor productivo (bake-off hecho, decisión pendiente).
- **Jerarquía ROF / organigrama** (`unidades.json` no existe).
- **Validación cruzada total comprobantes vs MONTO RECIBIDO** del Anexo 3.
- **Ventana temporal del viaje** vs fechas de comprobantes.
- **Filtro comprobante real vs consulta SUNAT anexa** (diseñado, no implementado).

---

## 2. PIPELINE COMPLETO DEL SISTEMA

### Flujo canónico (fuente: `docs/AGENT_RULES.md §4`)

```
INGESTA
  → OCR / TEXTO (por página, text_reader v2)
  → CLASIFICACIÓN (classifier, 9 + 1 categorías)
  → EXTRACCIÓN (PASO 4.1 — piloto_field_extract_paso4)
  → RESOLUCIÓN DE IDENTIDAD (id_resolver: SINAD, SIAF, EXP, AÑO)
  → COMPROBANTES (detector + extractor, solo si tipo=rendicion)
  → CONSOLIDACIÓN (expediente.json schema v3)
  → VALIDACIONES (firmas_anexo3, solo si tipo=rendicion)
  → EXCEL (6 hojas: resumen, comprobantes, documentos, expedientes, errores, resolucion_ids)
```

### Módulos reales con responsabilidades

| Módulo | Archivo | LOC | Rol | Entrada | Salida |
|---|---|---|---|---|---|
| CLI principal | `scripts/ingest_expedientes.py` | 780 | Orquestador sub-comandos `scan / process / consolidate / export / run-all` | carpeta con PDFs | Excel + JSON consolidado |
| Scanner | `scripts/ingesta/scanner.py` | 127 | Copia PDFs a `procesados/{id}/source/` + metadata.json + SHA-1 | carpeta | `metadata.json` con hashes |
| Text Reader | `scripts/ingesta/text_reader.py` | 218 | OCR por página: PyMuPDF nativo; si <50 chars → Tesseract | PDF | `.txt` concatenado + `.meta.json` por página |
| Classifier | `scripts/ingesta/classifier.py` | 403 | 9 categorías regex: solicitud, oficio, anexo, factura, orden_servicio, orden_compra, pasaje, rendicion, otros (+tipo_desconocido) | texto | `tipo_detectado`, confianza, puntajes |
| Extractor (doc) | `scripts/ingesta/extractor.py` | 154 | Wrapper PASO 4.1 a nivel documento | texto + tipo | 10 campos + `texto_resumen` |
| ID Resolver | `scripts/ingesta/id_resolver.py` | 275 | Detecta SINAD, SIAF, EXP, AÑO, PLANILLA, PEDIDO, OFICIO | texto | candidatos con fuente |
| Consolidador | `scripts/consolidador.py` | 446 | Produce `expediente.json` schema v3 con scoring, flujo financiero | extractions/*.json + metadata.json | `expediente.json` |
| Detector comprobantes | `scripts/ingesta/comprobante_detector.py` | 346 | Segmenta rendición en bloques-de-comprobante (ventana 1-3 páginas) | texto concatenado | `list[BloqueComprobante]` |
| Extractor comprobantes | `scripts/ingesta/comprobante_extractor.py` | 192 | Aplica PASO 4.1 al texto de cada bloque + fallback OCR agresivo | bloques | `list[Comprobante]` |
| OCR región totales | `scripts/ingesta/ocr_region_totales.py` | 162 | Segunda pasada agresiva 500 DPI (solo comprobantes con campos vacíos) | PDF + página | texto re-OCR |
| Firmas Anexo 3 | `scripts/validaciones/firmas_anexo3.py` | 341 | Valida firmas: comisionado, jefe_unidad, vb_coordinador | texto rendición | `ValidacionFirmas` |
| Extractor fields | `scripts/piloto_field_extract_paso4.py` | 957 | Motor determinista central: regex tolerantes OCR + oráculo SON + cross-check físico 1.5× + validador suma | texto de bloque | dict 10 campos + traza |
| Excel export | `scripts/ingesta/excel_export.py` | 683 | 6 hojas con upsert por clave (`expediente_id, archivo, pagina_inicio, pagina_fin`) | ComprobanteExcel[] | `.xlsx` |
| OCR Baseline | `scripts/document_ocr_runner.py` | 299 | PyMuPDF + CLAHE multi-pasada + Tesseract | PDF | por página |
| OCR Adaptativo | `scripts/ocr_adaptive_engine.py` | 496 | Gating + fallback Tesseract→Docling→EasyOCR (PASO 3) | PDF | por página con motor elegido |
| Modelo | `scripts/modelo/expediente.py` | 165 | Dataclasses `Expediente`, `Comprobante`, `ResolucionId`, `FlujoFinanciero` | — | schema v3 |
| Patrones SUNAT | `scripts/ingesta/patrones_sunat.py` | 106 | Regex compartidos (cabeceras, series, soporte) | — | constantes |

### Dependencias internas

```
scripts/ingest_expedientes.py
├─ scripts/ingesta/scanner.py
├─ scripts/ingesta/text_reader.py → scripts/document_ocr_runner.py → pytesseract
├─ scripts/ingesta/classifier.py → scripts/ingesta/patrones_sunat.py
├─ scripts/ingesta/extractor.py → scripts/piloto_field_extract_paso4.py
├─ scripts/ingesta/id_resolver.py
├─ scripts/ingesta/comprobante_detector.py → classifier
├─ scripts/ingesta/comprobante_extractor.py → piloto_field_extract_paso4.py → ocr_region_totales.py
├─ scripts/consolidador.py → modelo/expediente.py
├─ scripts/validaciones/firmas_anexo3.py
└─ scripts/ingesta/excel_export.py → openpyxl

agent_sandbox/main.py
├─ agent_sandbox/pdf_rag.py → embeddings.py
├─ agent_sandbox/cross_encoder_rerank.py → sentence-transformers
├─ agent_sandbox/orchestrator.py → nodes/
└─ agent_sandbox/llm_client.py (opcional, OpenRouter)
```

---

## 3. PILOTO OCR (FUENTE DE VERDAD PARA MEDICIÓN)

**Ubicación:** `data/piloto_ocr/`

### Contenido verificado

| Ruta | Contenido |
|---|---|
| `MANIFEST_PILOTO.csv` | 3 filas: un PDF por fila |
| `raw/` | 3 PDFs: `rend-debedsar-amiquero-2026.pdf` (31 pp), `ri-debedsar-amiquero-2026.pdf` (1 p), `sol-viat-debedsar-2026.pdf` (7 pp) |
| `labels/` | **15 JSON** + `_PLANTILLA_pagina.json` (template) |
| `metrics/` | CSVs + informes markdown + 1 Excel (PASO 2) |
| `logs/` | `ocr_adaptive_log.txt`, `ocr_adaptive_metrics.jsonl` |

### Estructura del `MANIFEST_PILOTO.csv`

```csv
doc_id,archivo_raw_relativo,paginas_en_pdf,paginas_en_piloto,indices_paginas_en_pdf,notas
ri-debedsar-amiquero-2026,raw/ri-debedsar-amiquero-2026.pdf,1,1,1,...
sol-viat-debedsar-2026,raw/sol-viat-debedsar-2026.pdf,7,2,"1,2",...
rend-debedsar-amiquero-2026,raw/rend-debedsar-amiquero-2026.pdf,31,12,"5,7,8,13,15,17,19,21,23,25,27,29",...
```

Total páginas-piloto: 1+2+12 = **15** (coherente con N=15 de PASO 0).

### Schema JSON de labels (`piloto_ocr.v1`)

```json
{
  "schema_version": "piloto_ocr.v1",
  "doc_id": "...",
  "page_index": 1,
  "etiquetado_por": "ground_truth_texto_pdf",
  "fecha_etiquetado": "YYYY-MM-DD",
  "campos": {
    "ruc_emisor": "11 dígitos | null",
    "tipo_documento": "string | null",
    "serie_numero": "string | null",
    "fecha_emision": "YYYY-MM-DD | null",
    "moneda": "PEN | USD | null",
    "monto_subtotal": "decimal | null",
    "monto_igv": "decimal | null",
    "monto_total": "decimal | null",
    "ruc_receptor": "11 dígitos | null",
    "razon_social_emisor": "string | null",
    "requiere_revision": "boolean"
  },
  "notas": "string"
}
```

### Consistencia manifest ↔ labels

- Manifest declara: 15 páginas-piloto.
- Labels en disco: 15 JSON (excluyendo plantilla).
- ✓ Coherencia confirmada por conteo y spot-check (`rend-debedsar-amiquero-2026_p13.json` → doc_id y page_index coinciden con manifest).

---

## 4. MÉTRICAS Y RESULTADOS REALES

### PASO 1 — Baseline (2026-04-10, Windows)

**Fuente:** `data/piloto_ocr/metrics/baseline_paso1_20260410.csv`, `INFORME_PASO1_20260410.md`.

- Motor: `tesseract_baseline` via `scripts/document_ocr_runner.py`.
- 15 páginas-piloto procesadas.
- Tiempo total: ~14-17 s (Windows).
- CSV con columnas: `doc_id, page_index, campo, valor_gold, valor_pred, exactitud, motor, fecha_corrida`.

### PASO 2 — Bake-off (2026-04-10 inicial, 2026-04-13 Windows, 2026-04-14 WSL)

**Fuente preferente:** `INFORME_PASO2_REVISION_20260414_linux_wsl.md` (D-12: WSL es preferente para bake-off).

**Resumen 2026-04-10 (Windows, 3 motores):**

| Motor | Macro F1 (eval) | Celdas correctas/117 | s/página |
|---|---|---|---|
| `tesseract_baseline` | **0.6667** | 78/117 | 0.012 |
| `docling` | 0.5897 | 69/117 | 2.119 |
| `easyocr_raster` | 0.5641 | 66/117 | 15.128 |

**Revisión 2026-04-14 WSL (preferente D-12):**

| Motor | P macro | R macro | **F1 macro** | s/página | % págs. fallo |
|---|---|---|---|---|---|
| `tesseract_baseline` | 0.9833 | 0.6572 | **0.7388** | 0.0249 | 100.0 |
| `docling` | 0.9833 | 0.5761 | 0.6852 | 3.1312 | 100.0 |
| `paddleocr` | 0.9733 | 0.5422 | 0.6194 | 2.2201 | 100.0 |

**Nota crítica:** `% págs. fallo = 100%` significa que cada página tiene al menos un campo con exactitud 0 — NO que el motor falle totalmente. Es métrica estricta PASO 0.

**Ganador medido:** Tesseract (F1 = 0.7388), lo cual ancla D-16: el cuello de botella es **parsing**, no OCR (posteriormente matizado en D-22: tras OCR agresivo sin éxito, el nuevo bottleneck es **layout/geometría**).

### PASO 4 — Evaluación parsing (2026-04-14 WSL)

**Fuente:** `data/piloto_ocr/metrics/paso4_eval_linux_wsl/INFORME_PASO4_EVAL_20260414.md`.

- CSV detalle: `paso4_eval_detalle_20260414.csv`.
- Trazas JSON: `paso4_eval_trazas_20260414.json`.
- Versiones: `pre41` (previa) y `20260414` (post PASO 4.1).
- ⚠ NO CONFIRMADO si hay F1 agregado posterior al oráculo SON y validador tributario (mejoras de 2026-04-18 a 2026-04-21).

### Pipeline de comprobantes — cobertura real (post-2026-04-21)

| Expediente | Comp. | monto_total | bi_gravado | monto_igv | op_exonerada | op_inafecta |
|---|---|---|---|---|---|---|
| DEBE2026-INT-0316916 | 15 | 15/15 (100%) | 4/15 | 4/15 | 1/15 | 2/15 |
| DEBEDSAR2026-INT-0103251 | 10 | 10/10 (100%) | 4/10 | 10/10 | 0/10 | 0/10 |
| DIED2026-INT-0250235 | 29 | 14/29 (48%) | 2/29 | 5/29 | 3/29 | 3/29 |
| DIED2026-INT-0344746 | 32 | 29/32 (91%) | 11/32 | 18/32 | 16/32 | 13/32 |
| **Total** | **86** | **68/86 (79%)** | 21/86 (24%) | 37/86 (43%) | 20/86 (23%) | 18/86 (21%) |

**Recargo consumo:** 0 casos reales en el corpus (capacidad implementada y testada sintéticamente, latente).

### Errores típicos + causa raíz

- **Columnas pegadas Marcoantonio:** `OP. INAFECTA: 160.00` OCR lee `INAFECTA: 4160.00` (dígito de renglón superior contamina) — **causa: OCR en tabla densa**. Filtro 1.5× descarta el valor pero no lo recupera.
- **Boletas EB01 SUNAT:** imprimen `OP.GRAVADA: 0.00 / EXONERADA: 0.00 / INAFECTA: 0.00` sin base real — **causa: boleta simplificada, no OCR**.
- **Decimales truncados:** `S/ 80.0C`, `Si 4?.0;` — **causa: pixeles perdidos en escaneo original**, irrecuperable.
- **Razón social:** 6 casos con None o ruido (`SANCARLOS Abril 07, 2026`) — **causa: OCR captura header junto con fecha/logo**.

---

## 5. MOTOR DE OCR (DECISIONES TÉCNICAS)

### Decisión actual

- **Motor productivo:** Tesseract 5.4.0 (CPU-only).
- **Baseline:** `scripts/document_ocr_runner.py`.
- **Multi-pasada:** conservador-primero. Pasada 1 = CLAHE(2.0) + PSM auto. Si <60 chars o junk ratio >3% → pasada 2 (denoise + CLAHE 3.0 + unsharp); si sigue pobre → pasada 3 (auto-rotate OSD); última pasada = aggressive (upscale 2× + CLAHE 4.0).
- **OCR por página:** `scripts/ingesta/text_reader.py` invoca OCR SOLO si PyMuPDF nativo da <50 chars para esa página. Cache por SHA-1 del PDF.
- **OCR región totales (D-20):** `scripts/ingesta/ocr_region_totales.py`. Segunda pasada 500 DPI + 4 variantes × 2 PSM sobre comprobantes con campos tributarios vacíos. NO sobrescribe; solo llena huecos. Recuperación medida: 4/59 (6.8%).

### Cuándo usa OCR vs texto digital

```python
# En text_reader.py
if len(pagina.get_text("text")) >= 50:
    usar_texto_nativo()
else:
    aplicar_tesseract()
```

### Thresholds activos

- `_MIN_CHARS_PAGE_NATIVE = 50` (text_reader) — envía a OCR si nativo < 50.
- `_MIN_CHARS_FIRST_PASS = 60` (document_ocr_runner) — gatilla retry agresivo.
- `_MAX_JUNK_RATIO_FIRST_PASS = 0.03` — gatilla retry si >3% `\ufffd`.
- `_OCR_RENDER_DPI = 300` (baseline) / `500` (región totales agresiva).

### Fallback documentado (no activo en productivo)

- `scripts/ocr_adaptive_engine.py` (496 líneas) define gating Tesseract → Docling → EasyOCR. ⚠ NO CONFIRMADO si está wired al pipeline de comprobantes (parece usado solo en PASO 3 evaluaciones).

### Decisiones clave relacionadas (D-01 … D-23)

- **D-01** (Cerrada): rechazar VLM/LLM como OCR principal.
- **D-02** (Cerrada): pipeline híbrido preproc → OCR → reglas → fallback LLM acotado.
- **D-05** (Abierta): PaddleOCR como candidato futuro; decisión depende de métricas PASO 2 en GPU.
- **D-06** (Hecho): baseline `document_ocr_runner.py`.
- **D-11** (Documentada): OCR por regiones (ROI) como **línea futura**, no implementado.
- **D-12** (Cerrada): WSL/Linux preferente para bake-off PASO 2 (pero pipeline productivo corre en Windows CPU).
- **D-16** (2026-04-18): bottleneck = parsing, no OCR (después de ganar Tesseract bake-off).
- **D-20** (2026-04-21): OCR agresivo como 2da pasada no-destructiva, recuperación 4/59.
- **D-22** (2026-04-21): techo OCR global alcanzado, nuevo bottleneck = layout/geometría.

---

## 6. MOTOR DE EXTRACCIÓN (CRÍTICO)

### Arquitectura

- **100% determinista.** Regex + heurísticas + cross-checks. **NO hay LLM en extracción.**
- **Módulo central:** `scripts/piloto_field_extract_paso4.py` (957 líneas).
- **Trazabilidad:** cada campo extraído emite una regla aplicada + fragmento fuente (`trace_dict[campo]`).

### Campos clave extraídos

| Campo | Reglas principales | Tolerancias OCR |
|---|---|---|
| `ruc_emisor` | `\b(\d{11})\b` contextualizado al header | — |
| `serie_numero` | `[EFB]\d{3}-\d{2,8}` | — |
| `fecha_emision` | `YYYY-MM-DD` / `DD/MM/YYYY` / "DD de MES de YYYY" | — |
| `monto_total` | 6 reglas jerárquicas: `Total a pagar` > `Precio de Venta` > `IMPORTE TOTAL` > `IMPORTE A PAGAR` > `IT` / `I.T.` > `Total` (con lookbehind anti-`SUB`) | + oráculo SON (letras) como autoridad legal |
| `monto_igv` | `IGV` + variantes OCR: `IGY`, `15V`, `IBV`, `I5V`, `IOV` + `Total I.G.V.` | S↔5 parcial, I↔1 |
| `bi_gravado` | `Valor Venta / V.V. / VV` > `Op. Gravada` > `SUBTOTAL` > `Base Imponible` | Filtro anti-leyenda `$`/`Sin impuestos` |
| `op_exonerada` | `Op.\s*Exonerada[s]?` en línea | Plural aceptado |
| `op_inafecta` | `Op.\s*Inafecta[s]?` en línea | Plural aceptado |
| `recargo_consumo` | 5 patrones: `RECARGO AL CONSUMO`, `RECARGO`, `SERVICIO 10%`, `SERVCIO` (falta I), `SERVICE CHARGE` | O↔0 (CONSUMO ↔ C0NSUM0), I↔1 (SERVICIO ↔ SERV1C1O) |
| `razon_social_emisor` | Prioriza sufijos legales (S.A.C., S.R.L., E.I.R.L.) y filtra exclusiones (FACTURA, HTTP, direcciones) | — |

### Oráculo SON (clave del recall actual)

En facturas peruanas SUNAT es **obligatorio** imprimir el monto en letras: `SON: CIENTO SESENTA CON 00/100 SOLES`. El extractor incluye un parser español-a-número:

```python
# En _monto_desde_son()
m = re.search(r"\bSON\s*[:.]?\s*([A-Za-zÁÉÍÓÚÑ\s]+?)\s+(?:CON|Y)\s+(\d{1,3})\s*/\s*1\d{2}", ...)
# Diccionario _NUMEROS_ES con 50 palabras (cero..mil + compuestos)
```

Tolera: `CON` o `Y` antes de centavos; centavos con ruido OCR (`00/106` → 0); acentos. **Recuperó +21 montos vs baseline** (en los 4 expedientes).

### Cross-checks activos

1. **Físico 1.5×:** si un componente (bi / exo / ina / recargo) > total × 1.5 → descartado con traza `<campo>_descartado_por_crosscheck`. Corrige Marcoantonio con 460/4160.
2. **Suma informativo:** si `bi + igv + recargo ≠ total (±1.00)` → anota en traza `crosscheck_suma_difiere_{delta}`. NO modifica valores.
3. **SON override:** si `monto_total` extraído difiere del SON por >1.00 absoluto y >10% relativo → prefiere SON (convención legal).

### Validador tributario (D-19)

`_clasificar_tipo_tributario(bi, igv, exo, ina)` devuelve:

- `GRAVADA` si IGV>0 o bi>0 (sin exo/ina positivos)
- `EXONERADA` si op_exonerada>0 sin gravable
- `INAFECTA` si op_inafecta>0 sin gravable
- `MIXTA` si gravada + exo/ina positivos
- `NO_DETERMINABLE` si todos en 0 o None

**Suma esperada** depende del tipo. Para EXONERADA la suma es solo `op_exonerada + recargo` → no se exige `bi_gravado`.

### Estados de consistencia (D-19)

- `OK` si `|total - suma(componentes del tipo)| ≤ 1.00`
- `DIFERENCIA_LEVE` si 1.00 < |delta| ≤ 5.00
- `DIFERENCIA_CRITICA` si |delta| > 5.00 o componente > total+1 (violación física)
- `DATOS_INSUFICIENTES` si falta total o todos los componentes son 0/None

### Limitaciones actuales conocidas

- **Marcoantonio columnas pegadas:** OCR lee bien pero mezcla columnas → cross-check descarta valor pero no lo recupera.
- **Boletas EB01 simplificadas:** OCR correcto, pero PDF imprime ceros sin base real → `DATOS_INSUFICIENTES`.
- **`razon_social` con ruido:** 6 casos con headers capturados junto con fechas/logos.
- **Recargo consumo:** capacidad latente (0 casos en corpus).
- **`recargo_consumo`, `ISC`, `Otros Tributos`, `FISE`:** campos adicionales NO implementados por política (D-23 prohíbe nuevos campos hasta validación humana).

---

## 7. SISTEMA RAG

### Arquitectura (fuente: `docs/CURRENT_STATE_RAG.md`)

**Ubicación:** `agent_sandbox/`

| Capa | Implementación |
|---|---|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (fijo en código) |
| Índice | JSON local `agent_sandbox/index/index.json` con `INDEX_SCHEMA_VERSION=4` |
| Chunking | Schema 4 con corte por encabezados normativos (OBJETIVO, 6.4., artículo, numeral, anexo) |
| Recuperación | Coseno + score híbrido (semántica + keywords + tipo de chunk + intención léxica) |
| Pool | Multivista fijo: **6 semántica + 2 léxica + 2 estructural → top 10** |
| Rerank | Local heurístico + cross-encoder opcional |
| Cross-encoder | `BAAI/bge-reranker-v2-m3` (`max_length=1024`), **requiere CUDA**; sin GPU cae a torneo pairwise |
| Salida | Top-10 al caller con `score`, `confidence`, `chunk_id`, `fragmento` |

### Código principal

- `agent_sandbox/pdf_rag.py` (1993 líneas) — índice, chunking, búsqueda, multivista.
- `agent_sandbox/cross_encoder_rerank.py` (303 líneas) — CE BGE en GPU, pairwise fallback.
- `agent_sandbox/embeddings.py` (45 líneas) — envoltorio all-MiniLM-L6-v2.
- `agent_sandbox/main.py` (474 líneas) — CLI + benchmark.
- `agent_sandbox/orchestrator.py` (79 líneas) — pipeline LangGraph-like.
- `agent_sandbox/llm_client.py` (333 líneas) — cliente OpenRouter opcional.
- `agent_sandbox/nodes/` — razonamiento, validación, salida.

### Top-k real y parámetros

```python
K_POOL_SEMANTIC = 6
K_POOL_LEX = 2
K_POOL_STRUCT = 2
TOP_K_POOL = 10
_CE_BUCKET = 0.04
```

### Benchmark actual

- **Medido:** 12/18 top-1 tras chunking v4 (`main.py --rag-eval-benchmark`).
- **Regresión:** antes 16/18 con chunking previo. La migración a schema 4 mejoró estructura pero perdió 4 aciertos. Documentado en `CURRENT_STATE_RAG.md §3`.

### Casos problemáticos identificados (CURRENT_STATE_RAG.md §4)

- **Ítem #2** — ámbito/aplicación: gold en §2 ÁMBITO; mezcla con OBJETIVO y BASE NORMATIVA.
- **Ítem #4** — plazo/rendición: gold en 6.4.x; posible partición entre chunks.
- **Ítem #8** — reprogramaciones: gold en 6.5; fallo es ranking top-1, no ausencia.

### Cuello de botella RAG

**Estructural (chunking + alineación con PDF), no calidad del modelo.** Mejoras propuestas: corregir detección de encabezados 2-líneas, alinear cortes con secciones 6.x, reducir chunks basura en anexos.

### Integración con pipeline OCR

**NO EXISTE.** D-07 lo bloquea hasta cerrar PASO 7 (contrato de datos). El RAG y el pipeline OCR son líneas paralelas independientes.

---

## 8. REGLAS DEL PROYECTO (AGENT_RULES)

**Fuente completa:** `docs/AGENT_RULES.md` (204 líneas).

### Gobernanza

| Rol | Quién | Alcance |
|---|---|---|
| Decisor final | **Hans** | Aprueba fases, cambios de rumbo, push a remoto |
| Ejecutor principal (implementación) | **Claude Code** | Modifica archivos, commit/push bajo autorización |
| Apoyo documentación/diseño | **Cursor** | md/yaml/json descriptivos; SIN código ejecutable |
| Auditor / continuidad estratégica | **ChatGPT** | Validación de consistencia entre herramientas |

### Principio general

Los agentes deben basarse en **estado real del repositorio**, no en suposiciones ni memoria de sesiones previas. **No inventar arquitectura.** **No asumir implementaciones inexistentes.** **Antes de actuar sobre un recuerdo, confirmarlo.**

### Restricciones duras

- No modificar código sin instrucción explícita de Hans.
- No crear módulos fuera del pipeline existente sin diseño aprobado.
- No renombrar, mover, eliminar archivos sin justificación escrita.
- No usar `git push --force`, `git reset --hard`, `--no-verify`, `--no-gpg-sign` salvo pedido explícito.
- No introducir dependencias nuevas sin agregarlas a `requirements-ocr.txt` o el que corresponda.

### Restricciones de datos

- **No inventar datos.** Campo no extraíble → `null` con `confianza = 0`.
- **No forzar resolución en conflicto.** Evidencia ambigua → `CONFLICTO_EXPEDIENTE`.
- **Trazabilidad obligatoria.** Cada dato extraído debe registrar fuente (archivo, página, regla, fragmento).

### Pipeline canónico (orden no negociable)

Ver sección 2 de este documento.

### Reglas de alineación

- **No saltar pasos.** No añadir validaciones antes de que el paso correspondiente esté consolidado en `expediente.json`.
- **Aditivo, no destructivo.** Un paso nuevo se suma; no reescribe salidas públicas de pasos anteriores.
- **Desacoplado.** Cada paso debe poder desactivarse con `--skip-*`.
- **Idempotente.** Cache por SHA-1. Upsert por clave estable en Excel.

### Reglas de respuesta

- Evitar genéricos. Nombrar archivos, funciones, líneas, commits (`archivo:línea`, `hash 7 chars`).
- Basarse en archivos reales. Si se cita ruta, debe existir.
- Preguntar si hay ambigüedad.
- Diferenciar lo implementado de lo documentado.
- Conciso: resultado + contexto + siguiente paso.
- Marcar honestamente limitaciones.

### Política Excel (D-23, vigente desde 2026-04-21)

- Excel **NO se commitea automáticamente**.
- Protección local: `.gitignore` + `git update-index --skip-worktree`.
- Versionado solo con autorización explícita: `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`.
- Desproteger: `git update-index --no-skip-worktree <path>` → commit → re-proteger.

---

## 9. PROBLEMAS REALES IDENTIFICADOS

### OCR (verificados con métricas y código)

1. **Tesseract con tablas densas falla:** columnas ultra-compactas (Marcoantonio) se pegan — ningún preproc lo arregla.
2. **DNI tenue rotado (p9 0316916):** OSD no detecta orientación; el OCR devuelve ruido.
3. **Escaneos con pixeles truncados:** decimales `S/ 80.0C`, `Si 4?.0;` — información perdida en origen.
4. **SKY Airline boarding passes:** texto gris tenue extremo — 261-541 chars capturados vs legible para humano.
5. **Firmas manuscritas invisibles al OCR:** Tesseract no ve el trazo; solo etiquetas cercanas (`FIRMA COMISIONADO`).

### Extractor (verificados con Excel y traza)

1. **Marcoantonio p30/p38/p46/p54:** `op_inafecta` correcto leído como `0.00` cuando real es `160.00` (columna pegada).
2. **p42 San Carlos 0316916:** `op_exonerada=39.00` == total — sospechoso (restaurant nunca es exonerado), no descartado por cross-check (ratio 1.0 < 1.5×).
3. **p56 0316916 "Transportes Rioja":** `serie_numero=None` — regex no detecta `FT05-00017636` en texto ruidoso.
4. **6 razones sociales con ruido:** `SANCARLOS Abril 07, 2026 F001-00019843` en vez de `RESTAURANT SAN CARLOS E.I.R.L.`.
5. **`bi_gravado` + `op_exonerada` legítimo sobre-reportado:** si SUBTOTAL aparece y existe op_exonerada, bi_gravado puede capturar SUBTOTAL aunque la factura sea exonerada pura (riesgo documentado, no observado en corpus actual).

### Pipeline / Consistencia

1. **DIED-0250235 globalmente degradado:** 24/29 DATOS_INSUFICIENTES. OCR del PDF original muy pobre.
2. **5 comprobantes sin monto_total** (0250235: p34, p42, p46, p50, p54). Rompe cualquier validación posterior.
3. **Umbrales de `id_resolver` calibrados con 1 expediente:** recalibrar con ≥5 (pendiente, documentado en SESSION_STATE §A).

### Datos incompletos / inconsistencias

1. **`docs/estructura_minedu/unidades.json` no existe** — necesario para validar jerarquía ROF.
2. **ROF y Organigrama PDFs presentes pero sin catálogo operativo** (carpeta `ROF Y ORGANIGRAMA/` en gitignore).
3. **Matriz de validación de expediente (PASO 7) no existe formalmente.**
4. **Ground truth N=15 nunca re-ejecutado con mejoras de 2026-04-18 a 2026-04-21** → F1 actualizado del extractor sobre piloto ⚠ NO CONFIRMADO.

### Dependencias rotas o de riesgo

1. **Python 3.14** (verificado por `python --version`) — muy reciente, varias librerías pueden no tener wheels oficiales. `requirements-ocr.txt` declara `numpy>=1.24`, `pymupdf>=1.24`, sin pin superior.
2. **RTX 5090 Blackwell no usada:** OpenCV sin CUDA, Tesseract CPU, CE-BGE requiere CUDA pero no hay validación de su uso actual.
3. **Cross-encoder solo activo con GPU:** sin CUDA cae a pairwise, métricas pueden diferir entre dev y prod.

---

## 10. ESTADO DE PRODUCCIÓN (HONESTO)

### Clasificación: **PILOTO EN VALIDACIÓN HUMANA**

Justificación:

| Criterio | Estado | Razón |
|---|---|---|
| Pipeline ejecutable end-to-end | ✓ | `python scripts/ingest_expedientes.py run-all --src ...` funciona |
| Cobertura probada en >1 expediente | ✓ | 4 expedientes reales, 86 comprobantes |
| Métricas de calidad medidas | ⚠ parcial | PASO 2 F1 0.7388 sobre N=15; pero mejoras post-PASO 4.1 no re-medidas sobre piloto |
| Validación humana completada | ✗ | 70/86 con `flag_revision_manual=SI`, sin revisión hecha |
| Tests automatizados | ✗ | Directorio `tests/` vacío |
| Integración con RAG | ✗ | D-07 bloqueado hasta PASO 7 |
| Matriz de validación (PASO 7) | ✗ | No existe aún |
| Uso productivo autorizado | ✗ | README, D-23, NEXT_STEP lo prohíben explícitamente |

**Conclusión:** sistema **usable por un humano revisor** para acelerar control previo, pero **NO apto para decisiones automáticas ni para ser consumido por otro sistema sin revisión**.

---

## 11. QUÉ FALTA (ROADMAP REAL)

### Siguiente paso inmediato (blocker de la fase actual)

**VALIDACIÓN HUMANA DEL EXCEL** por parte de Hans.

Procedimiento (detallado en `NEXT_STEP.md`):

1. Abrir `data/piloto_ocr/metrics/validacion_expedientes.xlsx`.
2. Leer hoja `resumen`.
3. Filtrar hoja `comprobantes` por `flag_revision_manual = SI` (70 filas).
4. Revisar los 15 `DIFERENCIA_CRITICA` primero, contrastando PDF.
5. Luego los 55 `DATOS_INSUFICIENTES`.
6. Completar columnas humanas: `comentario_validacion`, `monto_correcto`, `ruc_correcto`, `proveedor_correcto`, `observaciones`, `validacion_final`.
7. Decisión explícita de Hans: aceptar, exigir mejoras, o pasar a siguiente fase.

### Siguiente paso crítico (post validación)

1. **Calibración**: re-correr PASO 4 eval sobre N=15 piloto con los patches de 2026-04-18 a 2026-04-21 (oráculo SON, regex tolerantes, cross-check, validador tributario). Medir si F1 sube.
2. **Filtro comprobante real vs consulta SUNAT anexa** (diseñado en SESSION_STATE §E, no implementado).
3. **Recalibrar umbrales `id_resolver`** con ≥5 expedientes reales.

### Mejoras estructurales (sin fecha, bloqueadas hasta cierre de fase)

- **PASO 7** formal: matriz de validación de expediente, checklist de negocio.
- **D-07** desbloqueo: integración OCR → agente RAG (requiere contrato de datos).
- **D-11** evaluar: OCR por regiones / ROI-based extraction si métricas lo justifican.
- **D-05** evaluar: PaddleOCR productivo en Windows + Blackwell CUDA 12.8.
- **Reembolsos por mayor gasto**: implementar desde docs/modulos/reembolsos/ (Cursor preparó todo).
- **Jerarquía ROF/organigrama**: construir `unidades.json` desde PDFs presentes.
- **Tests automatizados**: nada en `tests/` hoy.

### No abrir hasta cerrar validación humana (D-23 + NEXT_STEP)

- Nuevos campos tributarios (ISC, Otros Tributos, FISE, Monto de redondeo).
- Integración AG-EVIDENCE.
- Cambio de motor OCR global.
- Refactors al schema del Excel.
- **Integración del paquete `control_previo_viaticos` v2.1.0 desde el sandbox** (ver sección 16): el paquete existe, está probado (161 tests passing), pero su integración al repo requiere que Hans valide primero el Excel generado por el sandbox y autorice explícitamente.

---

## 12. ENTORNO TÉCNICO (verificado 2026-04-21)

| Aspecto | Valor | Comando de verificación |
|---|---|---|
| Sistema operativo | **Windows 11** (NT-10.0-26200) | `uname -a` |
| Shell | **Git Bash / MINGW64** (bash 5.2.37) | `echo $MSYSTEM` |
| Python | **3.14.3 Windows nativo** | `python --version` |
| Ruta Python | `C:\Python314\python.exe` | `python -c "import sys; print(sys.executable)"` |
| WSL | **No activo** en pipeline productivo | `echo $WSL_DISTRO_NAME` → vacío |
| Linux/Ubuntu | Usado para bake-off PASO 2 (D-12) | artefactos `*_linux_wsl` |
| **GPU** | **NVIDIA RTX 5090 Laptop**, 24 GB VRAM, driver 581.83 | `nvidia-smi` |
| **GPU en uso** | **NO usada** por pipeline | OpenCV 0 CUDA devices; Tesseract CPU |
| OpenCV | 4.13.0 | `cv2.__version__` |
| OpenCV CUDA | **0 dispositivos habilitados** | `cv2.cuda.getCudaEnabledDeviceCount()` → 0 |
| Tesseract | **5.4.0 CPU-only** | `tesseract --version` |
| PyMuPDF | >= 1.24.0 | `requirements-ocr.txt` |
| openpyxl | >= 3.1.0 | `requirements-ocr.txt` |
| sentence-transformers | >= 3.0.0 | `agent_sandbox/requirements.txt` |
| torch | >= 2.0.0 | `agent_sandbox/requirements.txt` |

**Implicación operativa:** pipeline 100% CPU Windows. RTX 5090 disponible pero no explotada. Detalle en D-21.

---

## 13. COMANDOS REALES DE EJECUCIÓN

### Pipeline de comprobantes (actual)

```bash
# Procesar un expediente nuevo end-to-end
python scripts/ingest_expedientes.py run-all \
    --src vision_rag_DEBE2026-INT-0316916 \
    --expediente-id DEBE2026-INT-0316916

# Regenerar Excel localmente sin reprocesar OCR
python scripts/ingest_expedientes.py export

# Reprocesar solo un expediente
python scripts/ingest_expedientes.py process --expediente-id <id>
python scripts/ingest_expedientes.py consolidate --expediente-id <id>
python scripts/ingest_expedientes.py export --expediente-id <id>

# Desactivar OCR agresivo (más rápido, menos recuperación)
python scripts/ingest_expedientes.py process --expediente-id <id> --skip-ocr-agresivo

# Forzar reprocesamiento ignorando cache OCR
python scripts/ingest_expedientes.py process --expediente-id <id> --force
```

### OCR baseline (PASO 1)

```bash
pip install -r scripts/requirements-ocr.txt
python scripts/document_ocr_runner.py
# Salida: texto y status por página de cada PDF en data/piloto_ocr/raw/
```

### Bake-off motores (PASO 2)

```bash
python scripts/bakeoff_paso2.py --tag windows    # o --tag linux_wsl
python scripts/bakeoff_paso2_human_export.py
# Produce: bakeoff_paso2_consolidado_YYYYMMDD.csv, bakeoff_paso2_revision_YYYYMMDD.xlsx
```

### Parsing PASO 4.1 evaluación

```bash
python scripts/piloto_paso4_eval.py
# Produce: paso4_eval_detalle_YYYYMMDD.csv, paso4_eval_trazas_YYYYMMDD.json
```

### RAG normativo (agent_sandbox)

```bash
# Desde agent_sandbox/
cd agent_sandbox/
python main.py                                  # sesión interactiva
python main.py --rag-eval                       # eval RAG sin LLM
python main.py --rag-eval-benchmark             # benchmark 18 preguntas
```

### Desproteger Excel para commit autorizado (D-23)

```bash
git update-index --no-skip-worktree data/piloto_ocr/metrics/validacion_expedientes.xlsx
git add data/piloto_ocr/metrics/validacion_expedientes.xlsx
git commit -m "evidence: Excel validado — <expedientes, estado, cobertura>"
git update-index --skip-worktree data/piloto_ocr/metrics/validacion_expedientes.xlsx
git push origin main
```

### Git checks obligatorios al iniciar sesión (AGENT_RULES §7)

```bash
git status
git log -1 --oneline
cat SESSION_STATE.md
cat docs/AGENT_RULES.md
```

---

## 14. MAPA DE ARCHIVOS DEL PROYECTO

```
vision_rag/
├── README.md                            # Estado actual abril 2026 (sección al inicio)
├── CURRENT_STATE.md                     # Estado técnico vivo (post 2026-04-21)
├── NEXT_STEP.md                         # Siguiente paso operativo (validación humana)
├── SESSION_STATE.md                     # Cierre sesión 2026-04-14 (referencia histórica)
├── CURSOR_HANDOFF.md                    # Handoff Cursor → Claude Code
├── .gitignore                           # Incluye entrada Excel (D-23)
│
├── scripts/                             # CÓDIGO EJECUTABLE (fuente de verdad)
│   ├── ingest_expedientes.py            # ← CLI principal (780 líneas)
│   ├── document_ocr_runner.py           # OCR baseline Tesseract + CLAHE
│   ├── ocr_adaptive_engine.py           # Gating Tesseract→Docling→EasyOCR
│   ├── consolidador.py                  # expediente.json schema v3
│   ├── piloto_field_extract_paso4.py    # ← Motor extractor (957 líneas, oráculo SON)
│   ├── piloto_field_extract_minimal.py  # Versión mínima PASO 2
│   ├── piloto_paso4_eval.py             # Evaluador PASO 4
│   ├── bakeoff_paso2.py                 # Bake-off motores OCR
│   ├── bakeoff_paso2_human_export.py    # Exportador Excel bake-off
│   ├── paso3_ab_mini.py                 # AB preprocesamiento
│   ├── gen_control_previo_manifests.py  # Manifiestos normativa
│   ├── requirements-ocr.txt             # pymupdf, opencv, pytesseract, openpyxl
│   ├── requirements-paso2.txt           # PASO 2: docling, paddleocr, easyocr
│   ├── ingesta/                         # Sub-pipeline
│   │   ├── scanner.py                   # Copia + SHA-1 + metadata
│   │   ├── text_reader.py               # OCR por página + cache
│   │   ├── classifier.py                # 9+1 categorías regex
│   │   ├── extractor.py                 # Wrapper extractor por doc
│   │   ├── id_resolver.py               # SINAD, SIAF, EXP, AÑO
│   │   ├── comprobante_detector.py      # Segmentación por bloques
│   │   ├── comprobante_extractor.py     # PASO 4.1 + OCR agresivo fallback
│   │   ├── ocr_region_totales.py        # NUEVO 2026-04-21: segunda pasada 500 DPI
│   │   ├── excel_export.py              # 6 hojas (resumen, comprobantes, …)
│   │   └── patrones_sunat.py            # Regex compartidos
│   ├── modelo/
│   │   └── expediente.py                # Dataclasses schema v3
│   └── validaciones/
│       └── firmas_anexo3.py             # Validación firmas determinista
│
├── agent_sandbox/                       # RAG NORMATIVO (línea paralela)
│   ├── main.py                          # CLI + benchmark
│   ├── pdf_rag.py                       # ← Núcleo RAG (1993 líneas, chunking v4)
│   ├── cross_encoder_rerank.py          # CE BGE opcional (GPU)
│   ├── embeddings.py                    # all-MiniLM-L6-v2
│   ├── orchestrator.py                  # Pipeline agente
│   ├── nodes/                           # Reasoning / validación / output
│   ├── llm_client.py                    # OpenRouter opcional (PASO 5)
│   ├── tools.py
│   ├── state.py
│   ├── agent_audit_log.py
│   ├── requirements.txt
│   ├── corpus/                          # PDFs normativos (gitignored)
│   ├── index/                           # Índice JSON generado (gitignored)
│   └── eval_questions.json              # 18 preguntas benchmark
│
├── data/
│   └── piloto_ocr/                      # GROUND TRUTH PASO 0
│       ├── MANIFEST_PILOTO.csv          # 3 PDFs, 15 páginas-piloto
│       ├── CHECKLIST_POBLADO.md
│       ├── PILOTO_OPERATIVO.md
│       ├── raw/                         # 3 PDFs del piloto
│       ├── labels/                      # 15 JSON + plantilla
│       ├── metrics/                     # PASO 1, 2, 3, 4 informes + CSVs
│       │   ├── validacion_expedientes.xlsx   # ← EXCEL DE VALIDACIÓN HUMANA (NO versionar, D-23)
│       │   ├── INFORME_PASO1_20260410.md
│       │   ├── INFORME_PASO2_20260410.md
│       │   ├── INFORME_PASO2_REVISION_20260413.md          # Windows
│       │   ├── INFORME_PASO2_REVISION_20260414_linux_wsl.md # Preferente D-12
│       │   ├── METRICAS_MINIMAS.md
│       │   ├── baseline_paso1_20260410.csv
│       │   ├── bakeoff_paso2_*_20260410.csv
│       │   ├── bakeoff_paso2_*_20260413.xlsx
│       │   ├── bakeoff_paso2_*_20260414_linux_wsl.xlsx
│       │   ├── paso2/ paso2_linux_wsl/                     # Textos por motor
│       │   ├── paso3_ab_linux_wsl/
│       │   └── paso4_eval_linux_wsl/                        # INFORME_PASO4_EVAL_20260414.md
│       └── logs/                        # ocr_adaptive_log.txt, *.jsonl
│
├── control_previo/                      # NORMATIVA + EXPEDIENTES (gitignored PDFs)
│   ├── README.md
│   ├── MANIFEST_INGESTION_TODO.csv
│   ├── 01_viaticos/                     # Categoría de negocio MINEDU
│   ├── 02_os_oc_pautas/
│   ├── 03_caja_chica/
│   ├── 04_encargos/
│   ├── 05_detracciones/
│   ├── 06_subvenciones/
│   ├── 07_referencia_institucional/
│   └── procesados/                      # ← SALIDAS DEL PIPELINE
│       ├── DEBE2026-INT-0316916/        # expediente.json, extractions/, ocr_cache/
│       ├── DEBEDSAR2026-INT-0103251/
│       ├── DIED2026-INT-0250235/        # Expediente piloto original
│       └── DIED2026-INT-0344746/
│
├── docs/                                # DOCUMENTACIÓN (fuente de verdad sobre decisiones)
│   ├── AGENT_RULES.md                   # ← Gobernanza agentes
│   ├── ROADMAP_PROYECTO.md              # ← PASO 0–7 + §11 líneas futuras
│   ├── DECISIONES_TECNICAS.md           # ← D-01 … D-23
│   ├── CURRENT_STATE_RAG.md             # Estado núcleo RAG
│   ├── ANALISIS_COMPROBANTES.md
│   ├── INGESTA_EXPEDIENTES.md
│   ├── RESOLUCION_EXPEDIENTE_ID.md
│   ├── VALIDACION_FIRMAS_ANEXO3.md
│   ├── GUARDARRAILES_AUDITORIA.md
│   ├── CONTROL_PREVIO_TAXONOMIA_EXPEDIENTES.md
│   ├── EXPEDIENTE_FGE2025-INT-1081440_ORGANIZACION.md
│   ├── MIGRACION_NORMATIVAS_2026-02-06.md
│   ├── CHANGELOG.md
│   ├── LLM_MASTER_CONTEXT.md            # ← ESTE ARCHIVO
│   └── modulos/
│       └── reembolsos/                  # Docs Cursor (sin implementación)
│           ├── reembolso_mayor_gasto_base.txt
│           ├── reembolso_mayor_gasto.md
│           ├── rules_reembolso.yaml
│           └── schema_reembolso.json
│
├── tests/                               # ⚠ VACÍO (sin tests automatizados)
├── output/                              # (gitignored)
├── normativa_control_previo/            # Copia de normativa (presente)
├── ROF Y ORGANIGRAMA/                   # PDFs estructura institucional (gitignored)
└── [carpetas drop-zone ad-hoc]          # DIED*/, vision_rag_DEBE*/ (gitignored)
```

---

## 15. HANDOFF PARA OTRA IA (CRÍTICO)

### Si eres otra IA leyendo este documento por primera vez

**Lee este bloque completo antes de proponer cualquier acción.**

### Contexto mínimo obligatorio

1. Este es `vision_rag`: pipeline OCR determinista + parsing + RAG normativo para control previo MINEDU.
2. La fase activa está **ABIERTA** — no ha sido validada por Hans (el usuario/decisor final).
3. El artefacto clave es `data/piloto_ocr/metrics/validacion_expedientes.xlsx`. Hans aún no lo revisó contra PDFs.
4. El JSON consolidado por expediente (`control_previo/procesados/<id>/expediente.json`) es la **fuente de verdad técnica**; el Excel es solo herramienta de revisión humana.

### Estado al 2026-04-22

- 4 expedientes procesados, 86 comprobantes.
- Cobertura `monto_total`: 79%. Cobertura `bi_gravado`: 24%. Cobertura `monto_igv`: 43%.
- 70/86 comprobantes requieren revisión manual (`flag_revision_manual=SI`).
- Último commit en `main`: `da06f9b`.
- Entorno: Windows + Git Bash + Python 3.14 + Tesseract CPU. RTX 5090 disponible pero **no usada**.

### Problema principal (priorizado)

1. **[BLOCKER] Validación humana pendiente.** Sin decisión de Hans sobre el Excel, la fase no cierra y ninguna mejora técnica tiene criterio de aceptación.
2. **[ALTO] 64% de comprobantes en `DATOS_INSUFICIENTES`** — el OCR captura ceros o vacíos. Root cause: layout/geometría (tablas densas, boletas simplificadas, decimales truncados). Ya se agotó el OCR global (D-22). Línea futura: ROI geométrico (D-11).
3. **[MEDIO] PASO 0 formalmente abierto** — checklist §9 sin fecha de cierre pese a tener 15/15 labels.
4. **[MEDIO] Ground truth nunca re-ejecutado con parches post-PASO 4.1** — el F1 0.7388 es del bake-off; mejoras de 2026-04-18 a 2026-04-21 (oráculo SON, cross-check, validador tributario) no se han medido sobre N=15.
5. **[BAJO] Tests automatizados: 0.** Directorio `tests/` vacío. Toda verificación es manual o visual contra Excel.

### Acciones que NO debes proponer

- Integrar LLM al extractor (viola filosofía R1, D-01).
- Cambiar motor OCR antes de cerrar validación humana (viola D-23, NEXT_STEP).
- Agregar campos tributarios nuevos (ISC, FISE, Otros Tributos) hasta cerrar fase.
- Commitear `data/piloto_ocr/metrics/validacion_expedientes.xlsx` sin autorización explícita de Hans (viola D-23).
- Force push, reset --hard, amend sobre main, skip hooks.
- Integrar OCR al agente RAG antes de PASO 7 (bloqueado por D-07).
- Refactorizar esquema del Excel (viola restricción de NEXT_STEP).
- Abrir módulo de reembolsos por mayor gasto como feature nueva.

### Acciones correctas si Hans pide avanzar

**Si Hans dice "validé el Excel" o equivalente:**
- Pedirle que confirme el estado: aceptar / exigir correcciones / cerrar fase.
- Seguir el procedimiento de D-23 para versionar el Excel si él lo autoriza: `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`.
- Actualizar `NEXT_STEP.md` con la decisión tomada.

**Si Hans pide medir mejoras de parsing sobre el piloto:**
- Re-correr `scripts/piloto_paso4_eval.py` contra `data/piloto_ocr/labels/` y comparar con `paso4_eval_detalle_20260414.csv`.
- No cambiar código, solo medir.

**Si Hans pide atacar los 55 DATOS_INSUFICIENTES:**
- Consultar D-22 primero. El OCR global ya no mejora nada.
- Evaluar uso de `pytesseract.image_to_data()` para obtener bounding boxes con Tesseract existente (cero dependencias nuevas).
- Solo si eso falla, recién considerar D-05 (PaddleOCR) con advertencia sobre compatibilidad Python 3.14 + CUDA Blackwell.

**Si Hans pide cerrar PASO 0 formalmente:**
- Verificar `ROADMAP_PROYECTO.md §9` (4 criterios) y rellenar fecha de cierre con commit dedicado.
- No reabrir scope.

### Primera acción sugerida (si no hay instrucción explícita)

**Lee estos 4 archivos en orden** antes de proponer cualquier cosa:

```
1. SESSION_STATE.md              (estado de último cierre, puede ser stale)
2. CURRENT_STATE.md              (estado vivo post 2026-04-21)
3. NEXT_STEP.md                  (siguiente paso operativo autorizado)
4. docs/AGENT_RULES.md           (reglas de comportamiento para agentes)
```

**Después ejecuta:**

```bash
git status
git log -1 --oneline
```

Si estas lecturas entran en conflicto entre sí, **pausa y pregunta** antes de actuar.

### Formato de respuesta esperado

- Conciso (ver AGENT_RULES §5.2).
- Citar archivos y líneas (`archivo:línea`, hash 7 chars).
- Marcar honestamente limitaciones.
- Diferenciar implementado de documentado.
- No resumir narrativamente al final.

---

---

## 16. SANDBOX AUDITOR `control_previo_viaticos` v2.1.0 — ESTADO AL 2026-04-22

> Bloque crítico. Si leíste hasta aquí, no te saltes esta sección: explica una pieza que NO vive en el repo pero que cualquier IA continuadora necesita conocer.

### 16.1 Qué existe en el sandbox (NO en el repo)

**Ruta del sandbox (fuera del repo `vision_rag`):**

```
C:\Users\Hans\Documents\Claude\Projects\INGENIERIA INVERSA_módulo_VIÁTICOS_vision_rag\
  ├── salida_cowork\
  │   └── vision_rag_control_previo_v2.zip             (paquete original Cowork v2.0.0)
  └── sandbox_test_cowork_v2\
      ├── vision_rag_control_previo_v2\                (paquete extendido a v2.1.0)
      │   ├── src\control_previo_viaticos\
      │   │   ├── rules\    (24 módulos: 10 heredados v2.0 + 14 nuevos v2.1)
      │   │   ├── io\       (json_loader, ocr_loader, excel_writer)
      │   │   ├── extractor.py
      │   │   ├── validator.py
      │   │   └── __init__.py
      │   ├── tests\        (19 archivos, 161 tests passing)
      │   ├── examples\run_example.py
      │   ├── schemas\expediente_audit.schema.json
      │   ├── docs\         (DETERMINISM_MANIFESTO, RULES, LIMITATIONS, INTEGRATION_GUIDE)
      │   └── CHANGELOG.md  (v2.0.0 + v2.1.0 documentadas)
      ├── output\
      │   ├── AUDIT_DEBE2026-INT-0316916.xlsx          (generado por v2.0, ~17 KB)
      │   ├── AUDIT_DEBE2026-INT-0316916.audit.json    (v2.0)
      │   ├── AUDIT_DEBE2026-INT-0316916_v2_1.xlsx     (generado por v2.1, ~14 KB)
      │   └── AUDIT_DEBE2026-INT-0316916_v2_1.audit.json (v2.1)
      ├── RESUMEN_PRUEBA_AISLADA.md                    (corrida v2.0 smoke)
      └── RESUMEN_IMPLEMENTACION_v2_1.md               (corrida v2.1 completa)
```

### 16.2 Qué hace el auditor (síntesis)

Motor **post-pipeline**. Consume `expediente.json` y `ocr_cache/*.txt` que el pipeline de `vision_rag` ya produce (en `control_previo/procesados/<id>/`). **No toca el pipeline. No hace OCR. No modifica JSONs. No decide veredicto.**

Genera un Excel de **papeles de trabajo** y un `audit.json` con:

- Clasificación de cada comprobante en 15 sub-categorías operativas → 4 clasificadores MEF (`2.3.2 1.2 1 Pasajes`, `2.3.2 1.2 2 Viáticos`, `2.3.1 3.1 1 Combustibles`, `2.3.2 7.11 99 Otros gastos de viaje`).
- Topes de movilidad DJ 6.4.18 (Aeropuerto regiones S/35, Terrapuerto regiones S/25, Mov local Lima S/45/día, Mov local regiones S/30/día).
- Tope diario S/320 (ESCALA-2) / S/380 (ESCALA-1).
- Tope DJ 30% del viático otorgado.
- DJ exclusiva para viáticos (no admite pasajes/combustible/otros).
- Plazo 10 días hábiles.
- Hospedaje multidía con distribución lineal determinista e invariante Σ = monto exacto al centavo.
- Tiempo efectivo con márgenes por tipo de traslado (aéreo 3+2 h, terrestre 2+1 h, vehículo oficial instalación-instalación).
- Detección de conflictos **CP > DJ > Anexo 3** (regla R18 del usuario): el comprobante prevalece, se marca qué documento corregir.
- Detección de anexos con numeración desfasada SIGA vs RSG 023-2026 (ejemplo real: DJ etiquetada como "Anexo 4" cuando vigente es Anexo 9).
- Detección `R-INFORME-DUPLICACION-LITERAL` (informe = plan de trabajo) por ventanas de 20 palabras con umbral 3 — **100% literal, sin similitud semántica**.
- Resumen por clasificador MEF con invariante **devolución mostrada ≥ 0** (excesos se reportan como observación, no como celda negativa).
- Observaciones con base legal literal de la Directiva 023-2026-MINEDU (numeral + inciso + base breve).

**Sigue 100% determinista:** regex + tablas cerradas + aritmética Decimal. Cero LLM, cero similitud, cero fallback heurístico. Sin match → `NO_DETERMINABLE` o `DATOS_INSUFICIENTES`.

### 16.3 Qué se verificó en el sandbox

| Verificación | Resultado |
|---|---|
| `pytest tests/ -v` en entorno real (Windows + Python 3.14.3) | **161/161 passing en 0.53 s** |
| Corrida contra expediente real `DEBE2026-INT-0316916` | **12 observaciones, 7 hallazgos, 18 conformes** |
| Detección de desfase SIGA | ✅ DJ del PDF etiquetada como ANEXO 4 vs vigente ANEXO 9 |
| Clasificación CPs | 6 ALIMENTACION · 6 HOSPEDAJE · 2 PASAJE_TERRESTRE · 1 NO_DETERMINABLE |
| Invariante I1 (Σ hospedaje = monto) | ✅ 30 casos probados |
| Invariante I2 (ninguna específica con devolución negativa) | ✅ |
| Invariante I3 (reproducibilidad bit-a-bit) | ✅ |
| Bug encoding Windows en `io/json_loader.py` | ✅ corregido (agrega `encoding="utf-8"`) |

### 16.4 Qué **NO** se hizo

- **No se copió nada del sandbox al repo.** El repo `vision_rag` **permanece intacto**. Ningún archivo de `scripts/`, `agent_sandbox/` o similar fue tocado.
- **No se añadió** subcomando `auditar` al CLI `scripts/ingest_expedientes.py`.
- **No se versionó** el paquete en git.
- **No se commiteó** ningún Excel generado en el sandbox.
- **Hans no ha validado visualmente** el Excel generado por v2.1.0 — eso es el próximo paso humano.
- **Hans pidió además un rediseño del Excel** para que parezca "papeles de trabajo" (4 hojas: `ANALISIS_VIATICOS`, `CHECKLIST_DOCUMENTOS`, `OBSERVACIONES_Y_HALLAZGOS`, `REGISTRO_DE_COMPRAS`, altura de fila 14.75, colores específicos). El diseño final del layout quedó **propuesto pero no implementado** — espera `DISEÑO EXCEL OK — AUTORIZADO` para reescribir `io/excel_writer.py` (solo presentación, sin tocar lógica).

### 16.5 Criterio exacto para integrar al repo

La integración al repo solo procede si se cumplen todas estas condiciones:

1. Hans abre el Excel del sandbox (`AUDIT_DEBE2026-INT-0316916_v2_1.xlsx`) y valida que:
   - Las 12 observaciones generadas son correctas (algunas pueden ser falsos positivos por OCR degradado — ver 16.6).
   - La clasificación MEF por comprobante es correcta.
   - Los topes y el resumen por específica cuadran con su criterio operativo.
   - El layout es adecuado para uso de papeles de trabajo (pendiente rediseño según el modelo HCP).
2. Hans autoriza explícitamente con frase equivalente a `AUTORIZADO INTEGRACIÓN AL REPO`.
3. Se aplica el procedimiento de integración previamente propuesto:
   - Copiar `src/control_previo_viaticos/` → `scripts/ingesta/control_previo_viaticos/`.
   - Copiar `tests/` → `tests/control_previo_viaticos/`.
   - Añadir subcomando `auditar` a `scripts/ingest_expedientes.py` (aditivo, no rompe existentes).
   - Correr pytest dentro del repo → esperar 161 tests passing.
   - Registrar `D-24` en `docs/DECISIONES_TECNICAS.md` documentando la adopción.
   - Agregar al `.gitignore` patrón `AUDIT_CP_Viaticos_*.xlsx` (respeta política D-23).
   - **No commitear los Excel generados** salvo autorización explícita tipo D-23.

### 16.6 Limitaciones conocidas y observadas (documentadas honestamente)

1. **Corrida actual de DEBE-0316916 dio falsos positivos de topes 6.4.18.** El OCR del Anexo 4 (DJ) del expediente está degradado; los regex de `dj_anexo3_conceptos.py` capturaron 13 ítems totalizando S/5056 cuando el real son ~S/165. Esto disparó `OBS-TOPE-6418-*-EXCEDIDO` incorrectamente. **La lógica está bien**; los importes de input son incorrectos. Se mitiga con calibración de regex en integración real (input del pipeline OCR real del repo debería ser más limpio que este OCR cache degradado).
2. **Distribución hospedaje cayó a fallback 1 noche** porque el `texto_resumen` de los CPs no contenía fechas ingreso/salida literales. Invariante I1 sigue probado sintéticamente (30 casos). En CPs con mejor texto_resumen funcionará la distribución real.
3. **Tiempo efectivo = None** porque el caller `run_example.py` no pasa `hora_salida / hora_regreso`. Esperado por diseño. En integración real al repo, el subcomando `auditar` extraerá esos datos del Anexo 1 / Anexo 3 SIGA.
4. **Informe vs Plan coincidencias = 13490** porque el caller pasa `ocr_rendicion` como plan y como informe (mismo texto). En integración real, separar Anexo 6 (plan) y Anexo 7 (informe) antes de llamar al comparador.
5. **Monto otorgado = 0** en la corrida; disparó `OBS-ERROR-DISTRIBUCION-MEF` falsos. En integración real, el caller extraerá el otorgado del Anexo 2 SIGA antes de invocar el auditor.

### 16.7 Catálogo de observaciones y reglas implementadas

**Observaciones nuevas v2.1** (+14 respecto a v2.0):
`OBS-CLASIF-CONFLICTO-MEF` · `OBS-CLASIF-CONFLICTO-SUBCAT` · `OBS-CLASIF-DUPLICACION-CP-DJ` · `OBS-DJ-CLASIF-INVALIDA` · `OBS-DJ-TOPE-30-EXCEDIDO` · `OBS-TOPE-6418-N1-EXCEDIDO` · `OBS-TOPE-6418-N2-EXCEDIDO` · `OBS-TOPE-6418-N3-EXCEDIDO` · `OBS-TOPE-DIARIO-320-EXCEDIDO` · `OBS-TOPE-SPURIO` · `OBS-ANEXO-VERSION-DESFASADA` · `OBS-INFORME-NO-SUSTENTA` · `OBS-HOSP-RANGO-FECHAS-INVALIDO` · `OBS-ERROR-DISTRIBUCION-MEF`.

**Hallazgos nuevos v2.1**:
`HALL-CLASIF-AMBIGUO` · `HALL-CLASIF-NO-DETERMINABLE` · `HALL-HOSP-FECHAS-NO-EXTRAIBLES` · `HALL-INFORME-NO-COMPARABLE` · `HALL-TIEMPO-EFECTIVO-HORA-NO-EXTRAIBLE`.

**Familias de reglas nuevas v2.1**:
`R-CLASIF-CP-*` (15) · `R-CLASIF-MEF` · `R-A3-EXTRAER-ITEMS` · `R-DJ-EXTRAER-ITEMS` · `R-DJ-SOLO-VIATICOS` · `R-DJ-30-PORC` · `R-TOPE-6418-N1/N2/N3` · `R-TOPE-SPURIO` · `R-TOPE-DIARIO-320` · `R-TIEMPO-EFECTIVO` · `R-HOSP-DISTRIBUCION-LINEAL` · `R-HOSP-FECHA-INGRESO/SALIDA` · `R-CONFLICTO-CP-A3-MEF/SUBCAT` · `R-CONFLICTO-CP-DJ-DUPLICADO` · `R-ANEXO-VERSION-VIGENTE` · `R-INFORME-DUPLICACION-LITERAL` · `R-RESUMEN-MEF-SIN-NEGATIVO` · `R-VINCULO-ACTIVIDAD` · `R-CONFIANZA-EXTRACCION`.

### 16.8 Al continuador — mantra operativo

1. El sandbox tiene código funcional, probado con 161 tests y ejemplo ejecutado contra un expediente real del repo (modo solo lectura).
2. **El repo `vision_rag` permanece intacto**. Verificar con `git status` al abrir la sesión.
3. Integración requiere autorización explícita. Sin autorización: no copiar archivos, no modificar `scripts/`, no commitear Excel generados.
4. Si Hans pide continuar la iteración del auditor, se itera **en el sandbox**, no en el repo.
5. Si Hans dice "validé el Excel del sandbox y autorizo integración", seguir el procedimiento 16.5. No antes.

---

---

## 17. VALIDACIÓN OCR DJ — CUELLO DE BOTELLA CONFIRMADO (2026-04-22)

Tras validación humana contra el PDF del expediente `DEBE2026-INT-0316916` y
análisis empírico del `ocr_cache/*.txt`, se confirma un diagnóstico que altera
las prioridades operativas de mejora:

### 17.1 Evidencia resumida

- **PDF real (validación humana):** 21 ítems DJ, total S/ 165.00.
- **OCR cache (Tesseract baseline):** 19 líneas con fecha en la región `ANEXO N°4`.
- **2 ítems enteros** se perdieron en la transcripción OCR de la página 2 del Anexo 4 (la página llega al OCR solo con header + intro, sin filas de datos).
- De los 19 visibles: **7 con importe bien formado** (`5.00`, `6.00`) + **12 con importe corrupto o ilegible** (`500`, `2500`, `ali`, `—`, `Te`, `OO`).
- El total impreso `I TOTAL Sé | 165.00` **sí aparece correctamente en el OCR** — el dato existe pero no se desglosa por fila.

### 17.2 Tipos de error OCR observados

| Tipo | Ejemplos literales del OCR | Cantidad |
|---|---|---|
| Punto decimal perdido | `MOVILIDAD 2500`, `MOVILIDAD 500` | 6 |
| Carácter ilegible en lugar de número | `MOVILIDAD ali`, `—`, `Te`, `OO` | 4 |
| Importe no transcrito | línea sin cifra tras `MOVILIDAD` | 2 |
| Año OCR erróneo | `24/03/2028` en primera fila (debería 2026) | 1 |
| Concepto recortado | `VILIDAD` por `MOVILIDAD` | 1+ |
| "TAX!" por "TAXI" | `TAX!`, `TAX)`, `TAX]` | múltiples |

### 17.3 Confirmación de que el parser está correcto

El parser post-fix
(`sandbox_test_cowork_v2/.../rules/dj_anexo3_conceptos.py::extraer_items_dj`)
captura **19 / 19** líneas visibles en el OCR, asigna `numero_item` (1..19)
y `pagina_pdf` (3) a cada una. Aplica regex estricto
`\d+[\.,\s]\d{2}` para importes, aceptando los 7 bien formados
(Σ S/ 53.04) y marcando los 12 restantes como `IMPORTE_ILEGIBLE_PENDIENTE`
para revisión humana. El saneamiento auxiliar `R-AUX-DJ-SANEAMIENTO`
activa **0 descartes**. El parser funciona correctamente sobre el input
que tiene.

### 17.4 Conclusión: OCR upstream es el cuello de botella

> El cuello de botella actual es **OCR Tesseract sobre la tabla del
> Anexo 4 del PDF de rendición**, no el parsing DJ ni el Excel. Ningún
> refinamiento adicional al parser puede recuperar los 2 ítems perdidos
> ni los 12 importes corruptos sin caer en heurística prohibida
> ("rescatar importes DJ mal leídos" fue explícitamente vetado). La
> corrección que cierra la brecha 19→21 ítems y S/53→S/165 es una
> **segunda pasada OCR focalizada en la región DJ** (patrón análogo a
> `scripts/ingesta/ocr_region_totales.py` ya existente para totales de
> CPs), con DPI elevada y preprocesado orientado a tablas. **Esa
> intervención vive en el repo `vision_rag`, fuera del sandbox**.

### 17.5 Implicación para el Excel de revisión humana

- El Excel sandbox `AUDIT_HUMANO_DEBE2026-INT-0316916.xlsx` reporta
  correctamente lo que el OCR expone: 19 ítems trazables, 7 legibles
  (Σ S/ 53.04) + 12 pendientes con importe 0.00 y observación
  `IMPORTE_ILEGIBLE_PENDIENTE`.
- Esa salida es **honesta y reproducible**, pero **no completa**.
  Completarla exige (a) mejorar el OCR upstream o (b) completar
  manualmente los 12 pendientes durante revisión humana.
- Ningún cambio adicional en el sandbox puede cerrar la brecha sin
  tocar el pipeline del repo.

### 17.6 Evidencia completa

Ver `docs/evidencia/ocr_dj_diagnostico_2026-04-22.md` para el detalle
con volcado literal del OCR, conteos, clasificación de errores y
referencias cruzadas de archivos.

---

**Fin del documento.** Este archivo debe regenerarse manualmente cuando el estado real del proyecto cambie sustancialmente (nueva fase, nueva decisión D-24+, cambio de entorno, cierre de validación humana, integración del sandbox).
