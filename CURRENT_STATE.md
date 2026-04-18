# SANTO_GRIAL — Estado actual del proyecto

> Documento vivo para retomar el trabajo sin contexto externo.  
> **Entorno experimental**, separado de **AG-EVIDENCE**; **sin integración** con AG-EVIDENCE por ahora.

---

## ESTADO ACTUAL

- **RAG normativo** operativo sobre PDFs en `agent_sandbox/corpus/` (embeddings locales, índice JSON).
- **Recuperación de la sección OBJETIVO**: chunk dedicado con `tipo=objetivo`, texto que incluye `1. OBJETIVO` y párrafo normativo (~p. 4 en la directiva de viáticos de referencia).
- **Separación índice vs contenido**: el chunking en `pdf_rag.py` evita mezclar tabla de contenidos con el cuerpo (corte al salir del TOC hacia OBJETIVO, numeración partida en líneas, flush de buffer).
- **Ranking por intención**: si la consulta menciona explícitamente `objetivo` (y análogo para artículo/numeral con acentos normalizados), se aplica multiplicador sobre el score ya híbrido (coseno + keywords + ajuste por tipo). El factor para `objetivo` está calibrado para que consultas como “objetivo de la directiva…” recuperen el chunk correcto por delante de anexos muy largos.
- **Agente — fallback a RAG**: en `reasoning_node.py`, si el clasificador no propone herramienta, la acción efectiva es `buscar_en_pdf` (sin terminar en “sin tool”).
- **Validación flexible**: en `validation_node.py`, la consulta se acepta si tiene longitud razonable (`> 5` caracteres tras trim); no se bloquea por envelope vacío de fragmentos.
- **Respuesta legible**: en `output_node.py`, salida tipo “Respuesta + Fuente + chunk_id/confidence + fragmento recuperado + resumen de otros hits”, con heurísticas regex sobre el texto recuperado (sin LLM extra en ese paso).

**Qué funciona al usar** `python main.py` **o** RAG eval: el sistema puede **responder preguntas normativas reales** con **evidencia** (archivo y página).

---

## PROBLEMAS RESUELTOS (reciente)

| Problema | Enfoque |
|----------|---------|
| Chunk mezclando índice y contenido | Cortes en stream, tokens diferidos “1.” + OBJETIVO, flush al salir del índice |
| OBJETIVO no detectado / no tipado | Normalización de línea, regex de encabezado, reglas TOC vs cuerpo |
| Ranking incorrecto (anexos ganaban) | Boost por intención léxica en la consulta tras el score existente |
| Agente bloqueando consultas | Fallback obligatorio a `buscar_en_pdf`; validación permisiva por longitud de consulta |
| Respuestas poco usables (solo listado técnico) | `output_node` con extracto heurístico + fuente + trazabilidad |

---

## RESULTADO ACTUAL

El sistema, en condiciones normales de corpus e índice generado:

- **Responde** preguntas normativas con un **extracto** basado solo en texto recuperado.
- **Devuelve evidencia**: archivo, página(s), y metadatos útiles (`chunk_id`, `confidence` cuando existen).
- **No inventa** norma: la capa nueva no añade LLM de generación sobre el RAG; el contenido citado sale del corpus indexado.
- **Tolera** formulaciones imperfectas gracias al fallback a RAG y a la validación por longitud mínima.

---

## LIMITACIONES ACTUALES

- **Volumen de salida**: aún se incluye fragmento largo y listado de otros hits; puede sentirse “verboso”.
- **Heurística de extracto**: patrones regex; no es NLP profundo ni resumen semántico.
- **Interfaz**: consola / CLI; no hay UI web dedicada.
- **Dependencias**: embeddings (p. ej. `sentence-transformers`), posible `OPENROUTER_*` para el nodo de razonamiento con LLM cuando se usa el agente completo.
- **Índice**: depende de PDFs y de reconstruir `index.json`; extracción PyMuPDF sigue sujeta a calidad del PDF.

### Línea OCR / extracción documental (no es el RAG normativo)

- Roadmap obligatorio: **`docs/ROADMAP_PROYECTO.md`** (**PASO 0 → 7**). OCR sigue ese orden; el RAG normativo es **PASO 6** y es independiente del piloto de facturas.
- **PASO 0** operativo: **§4.1–4.3** (N=15 páginas, 11 campos, `piloto_ocr.v1`, métricas §4.3); checklist de cierre **§9**; datos en **`data/piloto_ocr/`**.
- Script baseline: `scripts/document_ocr_runner.py`. **Sin cierre de §9**, PASO 1 no tiene tabla de métricas **comparable** (solo pruebas ad hoc).
- **Pasos operativos:** **`data/piloto_ocr/CHECKLIST_POBLADO.md`** · detalle **`data/piloto_ocr/PILOTO_OPERATIVO.md`**.
- **Bloqueos** hasta PASO 0 cerrado: ver roadmap **§5.2** (bake-off formal, integración OCR–agente, subvención productiva).

### Infraestructura de validación humana (alimenta PASO 0; pre-PASO 7)

- **Desde 2026-04-14**: pipeline de ingesta de expedientes reales que produce un Excel revisable por humanos. No sustituye el piloto formal; lo acelera generando ground truth asistido sobre expedientes reales.
- **Flujo y uso:** `docs/INGESTA_EXPEDIENTES.md`.
- **Módulos:** `scripts/ingesta/{scanner,text_reader,classifier,extractor,excel_export}.py`, CLI `scripts/ingest_expedientes.py`.
- **Primer caso real:** `DIED2026-INT-0250235` (viáticos LILIANA CHAVEZ TERRONES, 2 PDFs — planilla + rendición consolidada). Resultado en `data/piloto_ocr/metrics/validacion_expedientes.xlsx`.
- **No inventa datos**: campos sin señal → `None` con confianza 0. Override consolidado trazable para PDFs de rendición con facturas anidadas.

---

## SIGUIENTE PASO (recomendado)

1. **Cerrar PASO 0** según **`docs/ROADMAP_PROYECTO.md` §9** (15 JSON + manifest).
2. **PASO 1** baseline y CSV en `data/piloto_ocr/metrics/`.
3. En paralelo (menor prioridad): simplificar `output_node` / UX según lista histórica abajo.
4. **Más adelante**: AG-EVIDENCE — no integrar hasta contrato de datos.

**Backlog RAG/UX (sin bloquear OCR):**

1. Simplificar `output_node`: respuesta más corta, modo verbose.
2. Reducir longitud por defecto del bloque principal y fragmentos secundarios.
3. Mejorar UX (env, flags CLI, UI ligera).

---

## Pipeline de comprobantes — estado técnico (2026-04-18)

### Expedientes validados en esta ronda

| Expediente | Comp. | RUC | Razón | Serie | Fecha | monto_total | bi_gravado | monto_igv | op_exonerada | op_inafecta |
|---|---|---|---|---|---|---|---|---|---|---|
| **DIED2026-INT-0344746** (nuevo) | 32 | 32/32 | 32/32 | 32/32 | 32/32 | 24/32 (75%) | 9/32 (28%) | 15/32 (47%) | 16/32 (50%) | 13/32 (41%) |
| DIED2026-INT-0250235 (piloto) | 29 | 29/29 | 29/29 | 29/29 | 18/29 | 8/29 | 2/29 | 4/29 | 3/29 | 3/29 |
| DEBEDSAR2026-INT-0103251 (2do) | 10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 4/10 | 10/10 | 0/10 | 0/10 |

### Qué funciona (100% estable)

- **Detección y segmentación de comprobantes** (detector + enriquecimiento CPE): identidad y número de comprobante correctos en los 3 expedientes.
- **RUC / razón social / serie_numero**: 100% en los 3 expedientes.
- **fecha_emision**: 100% en los 2 expedientes con OCR limpio (`DIED-0344746`, `DEBEDSAR-0103251`); 62% en piloto por OCR crasheado en 7 páginas.
- **monto_total**: regex flexible con paréntesis, `S/` opcional, orden libre con `:`. Captura `IMPORTE TOTAL (S/) 90.00`, `Total : S/ 200.00`, `Importe Total : 60.00`. Lookbehind evita capturar `SUB TOTAL`.

### Qué es parcial (cobertura dependiente de emisor)

- **`bi_gravado`** (nuevo): extracción determinista con prioridad `Valor Venta` > `Op. Gravada` (sin leyenda `$`/`Sin impuestos`) > `SUBTOTAL` > `Base Imponible`. Cobertura ~28% en `DIED-0344746` — residuales son facturas/boletas donde el emisor no imprime desglose contable (ausencia estructural, no fallo OCR).
- **`monto_igv`** (mejorado): regex flexible `\bIGV\s*[:.]*…`. Captura formatos `IGV:`, `IGV: S/`, `IGV 0.00`. Residuales en `DIED-0344746`: 2 casos con formato raro no cubiertos — `IGV: I.G.v. S/ 2.57` (etiqueta duplicada) y `IGV: [10.5%] 19.00` (porcentaje entre etiqueta y valor).
- **`op_exonerada`** / **`op_inafecta`** (nuevos): extracción línea por línea con filtro anti-leyenda (`$`, `Sin impuestos`). Boletas SUNAT al 100% con bloque tributario completo (incluye `0.00` legítimo para renglones que no aplican).

### Comportamiento observado en Excel

- **Archivo único**: `data/piloto_ocr/metrics/validacion_expedientes.xlsx`.
- **El export sobrescribe** el Excel con el último expediente procesado (no acumulativo). Para ver un expediente específico: `python scripts/ingest_expedientes.py export --expediente-id <X>`.
- **Columnas humanas preservadas**: `monto_correcto`, `ruc_correcto`, `proveedor_correcto`, `observaciones`, `validacion_final`.
- **Nuevas columnas de sistema** en hoja `comprobantes`: `bi_gravado`, `op_exonerada`, `op_inafecta` (insertadas entre `monto_igv` y `confianza`).

### Qué sigue inconsistente (residuales conocidos)

- `monto_total` residual ~25% global: páginas con OCR crasheado (piloto) o decimales sin ancla (transportes CRUZ).
- `monto_igv` residual ~50% en `DIED-0344746`: mitad por ausencia estructural + 2 casos con formato OCR raro no cubierto.
- `bi_gravado` residual ~70% en `DIED-0344746`: principalmente facturas simples sin desglose.
- `op_exonerada` / `op_inafecta` residual en facturas: muchas no imprimen esos renglones cuando no aplican (ausencia estructural, no bug).

### Archivos del pipeline — última tocada

- `scripts/piloto_field_extract_paso4.py` — extractor PASO 4.1 (funciones `_bi_gravado`, `_grab_op`, regex `monto_igv` flexible, regex `monto_total` flexible).
- `scripts/modelo/expediente.py` — dataclass `Comprobante` con `bi_gravado`, `op_exonerada`, `op_inafecta`.
- `scripts/consolidador.py` — propagación al JSON consolidado.
- `scripts/ingesta/comprobante_extractor.py` — mapeo fields → Comprobante.
- `scripts/ingesta/excel_export.py` — columnas `bi_gravado`, `op_exonerada`, `op_inafecta` en hoja comprobantes.
- `scripts/ingest_expedientes.py` — relleno de las nuevas columnas.

---

## Políticas operativas, vocabulario tentativo y riesgos (2026-04-18)

Esta sección complementa las decisiones formales de [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md) (D-13…D-17) con convenciones operativas y riesgos reconocidos que **aún no son decisiones cerradas**.

### Convenciones operativas adoptadas

- **Mensaje de commit de evidencia**: cuando se versiona un Excel regenerado o cualquier artefacto binario producto de una corrida, el mensaje del commit debe describir **exactamente** qué expediente(s) refleja. Ejemplo incorrecto: `"metricas de 3 expedientes"` cuando el Excel solo contiene el último. Ejemplo correcto: `"chore(evidencia): Excel regenerado para DIED-0344746 (32 comp, 24/32 monto, 16/32 op_exonerada)"`.
- **Una validación pendiente no se documenta como cerrada**: si el usuario dice "no estoy cerrando etapa", CURRENT_STATE y NEXT_STEP deben reflejarlo. Ver D-15.

### Vocabulario tentativo — estados de expediente

Uso operativo (no es todavía un campo del JSON ni del Excel; es vocabulario humano para describir dónde está cada expediente):

| Estado | Significado |
|---|---|
| `tecnicamente_procesado` | El pipeline corrió `run-all` sin error; JSON consolidado existe. |
| `pendiente_validacion_excel` | Procesado y exportado al Excel, pero sin revisión humana contra evidencia externa. |
| `validado_manual_parcial` | Revisión humana iniciada; algunas filas del Excel con columnas humanas llenas. |
| `validado_manual_final` | Revisión humana completa; `validacion_final` llena para todas las filas. |

**Mapeo actual de los 3 expedientes** (al 2026-04-18):

| Expediente | Estado operativo |
|---|---|
| `DIED2026-INT-0250235` (piloto) | `validado_manual_parcial` (ground truth ya construido en PASO 0) |
| `DEBEDSAR2026-INT-0103251` (2do / robustez) | `tecnicamente_procesado` |
| `DIED2026-INT-0344746` (validación manual en curso) | `pendiente_validacion_excel` — siguiente paso según `NEXT_STEP.md` |

### Vocabulario tentativo — roles de expediente de prueba

| Rol | Uso | Ejemplo actual |
|---|---|---|
| **Piloto** | Ground truth original para construir y calibrar el pipeline | `DIED-0250235` |
| **Robustez** | Segundo expediente para probar generalización de los fixes | `DEBEDSAR-0103251` |
| **Validación manual** | Expediente en curso donde se contrasta contra evidencia externa (cowork) | `DIED-0344746` |
| **Regresión** | Cualquiera de los anteriores, re-ejecutado tras un cambio de código para confirmar 0 regresiones | Los 3 se usan así |

### Riesgos reconocidos (sin acción inmediata)

- **Crecimiento transversal del pipeline**: cada campo nuevo (ej. `bi_gravado`, `op_exonerada`) toca **6 archivos** (`piloto_field_extract_paso4.py`, `modelo/expediente.py`, `consolidador.py`, `comprobante_extractor.py`, `excel_export.py`, `ingest_expedientes.py`). Riesgo de regresión silenciosa si se descuida el alcance. **Mitigación actual**: re-ejecutar los 3 expedientes tras cada cambio y verificar cobertura de todos los campos estables. **Acción pendiente**: no hay plan de refactor (fuera de alcance); registrado como riesgo.
- **Excel binario versionado**: ver D-17.
- **Interpretación semántica como cuello de botella**: ver D-16.

### Recomendaciones pendientes (no adoptadas todavía)

- Formalizar los estados de expediente como campo del `expediente.json` — hoy es solo vocabulario humano.
- Definir umbral cuantitativo para migrar el Excel de evidencia versionada a artefacto de salida (D-17).

---

## GOBERNANZA OPERATIVA (vigente desde 2026-04-14)

| Rol | Quién | Alcance |
|-----|-------|---------|
| **Decisor final** | Hans | Aprueba fases, cambios de rumbo, push a remoto |
| **Ejecutor principal** | Claude Code | Modifica archivos, hace commit y push — siempre bajo decisión de Hans |
| **Apoyo secundario** | Cursor | Ejecución/documentación operativa cuando Hans lo convoque |
| **Auditor / continuidad estratégica** | ChatGPT | Control de fase, validación de consistencia entre herramientas |

**Regla:** Claude Code puede ejecutar cambios en el repo (edición, commit, push) pero **no** toma decisiones de alcance ni abre fases sin aprobación explícita de Hans.

---

## REGLA IMPORTANTE

- **SANTO_GRIAL** = laboratorio / sandbox normativo (RAG + agente modular bajo `agent_sandbox/`).
- **AG-EVIDENCE** = línea de producto separada; **no** asumir enlaces de código ni despliegue compartido hasta decisión explícita.

---

## Referencia rápida de rutas

| Qué | Dónde |
|-----|--------|
| Roadmap PASO 0–7, bloqueos, checklist §9 | `docs/ROADMAP_PROYECTO.md` |
| Decisiones D-01…D-09 | `docs/DECISIONES_TECNICAS.md` |
| Piloto OCR (ground truth) | `data/piloto_ocr/` |
| RAG + índice | `agent_sandbox/pdf_rag.py` |
| Agente (orquestación) | `agent_sandbox/orchestrator.py`, `agent_sandbox/main.py` |
| Razonamiento / fallback RAG | `agent_sandbox/nodes/reasoning_node.py` |
| Validación | `agent_sandbox/nodes/validation_node.py` |
| Salida | `agent_sandbox/nodes/output_node.py` |
| Corpus PDF | `agent_sandbox/corpus/` |
| Índice generado | `agent_sandbox/index/index.json` |

---

## Repositorio Git (cierre de sesión)

- **Rama:** `main`. **Último commit:** ejecutar `git log -1 --oneline` en la raíz del proyecto.
- **`git push`:** remoto típico `origin` → `main` (ver `git remote -v`).

- En Windows, el repo usa `git config core.longpaths true` (evita fallos con rutas muy largas en carpetas de análisis o corpus).

---

*Última actualización: 2026-04-18 — pipeline de comprobantes extendido: bi_gravado + op_exonerada + op_inafecta agregados; monto_igv y monto_total con regex flexible; validado en 3 expedientes reales; 0 regresiones. Agregadas decisiones D-13…D-17 y políticas operativas (JSON fuente de verdad, política NULL, vocabulario tentativo de estados). Siguiente paso: validación de Excel vs cowork — ver `NEXT_STEP.md`.*
