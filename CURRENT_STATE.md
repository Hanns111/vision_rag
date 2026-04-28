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

## Entorno real de ejecución (verificado 2026-04-21)

| Aspecto | Valor |
|---|---|
| Sistema operativo | Windows 11 (NT-10.0-26200) |
| Shell de trabajo | Git Bash / MINGW64 (`bash 5.2.37`) |
| Python | 3.14.3 Windows nativo (`C:\Python314\python.exe`) |
| GPU instalada | **NVIDIA GeForce RTX 5090 Laptop** (24 GB VRAM, driver 581.83) — **NO usada por el pipeline actual** |
| OpenCV | 4.13.0 con **0 dispositivos CUDA habilitados** (compilado sin CUDA) |
| Tesseract | 5.4.0 — **CPU-only por diseño** |
| WSL / Linux nativo | **no activo** en la ejecución actual |

**Implicación operativa**: el pipeline corre 100% en CPU sobre Windows + Git Bash. La RTX 5090 está presente pero ninguna capa del sistema la explota hoy (D-05 PaddleOCR sigue abierta como opción futura; D-12 preferencia WSL aplica a bake-off PASO 2, no al pipeline actual).

---

## Pipeline de comprobantes — estado técnico (2026-04-21)

> **Estado de fase:** Excel final preparado para revisión humana, **fase NO cerrada**.
> Pendiente validación manual contra PDFs (ver [`NEXT_STEP.md`](NEXT_STEP.md)).
>
> **PRE-PASO 4.5 (2026-04-27):** código preparado para schema `expediente.v4` (persistencia
> de `ruc_receptor` + 3 campos tributarios calculados en el consolidador). **Artefactos
> reales aún NO regenerados** — los `expediente.json` en `control_previo/procesados/` y el
> Excel `validacion_expedientes.xlsx` siguen en formato pre-v4. La regeneración controlada
> de 1 expediente piloto a v4 requiere autorización explícita (ver [`NEXT_STEP.md`](NEXT_STEP.md) y D-24).

### Expedientes procesados (86 comprobantes, 4 expedientes)

| Expediente | Comp. | RUC | Razón | Serie | Fecha | monto_total | bi_gravado | monto_igv | op_exonerada | op_inafecta | recargo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **DEBE2026-INT-0316916** (nuevo, 2026-04-21) | 15 | 15/15 | 9/15 | 14/15 | 12/15 | 15/15 (100%) | 4/15 | 4/15 | 1/15 | 2/15 | 0/15 |
| DIED2026-INT-0344746 | 32 | 32/32 | 32/32 | 32/32 | 32/32 | 29/32 (91%) | 11/32 | 18/32 | 16/32 | 13/32 | 0/32 |
| DIED2026-INT-0250235 (piloto) | 29 | 29/29 | 29/29 | 29/29 | 18/29 | 14/29 (48%) | 2/29 | 5/29 | 3/29 | 3/29 | 0/29 |
| DEBEDSAR2026-INT-0103251 (2do) | 10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 (100%) | 4/10 | 10/10 | 0/10 | 0/10 | 0/10 |

*recargo_consumo en corpus real: 0 casos (capacidad implementada y testeada sintéticamente; se activará con facturas que impriman "RECARGO AL CONSUMO" o "SERVICIO 10%").*

### Qué funciona (estable tras refactor de parsing 2026-04-21)

- **Detección y segmentación de comprobantes** (detector + enriquecimiento CPE): identidad y número de comprobante correctos en los 4 expedientes.
- **RUC / razón social / serie_numero**: ~100% en los 4 expedientes (salvo p56 0316916 con serie None por OCR roto).
- **fecha_emision**: 100% en 3 expedientes con OCR limpio; 62% en piloto DIED-0250235 por OCR crasheado.
- **monto_total**: regex flexible + **oráculo SON en letras** (convención peruana obligatoria) + alias `I.T.`/`IT`. Cobertura global: 68/86 (79%) — recuperó +21 montos vs baseline pre-SON.
- **Parsing tributario con jerarquía conceptual (D-18, 2026-04-21)**: separa campos base (`SUBTOTAL`, `V.V.`, `Base Imponible`) de componentes tributarios (`Op.Gravada/Exonerada/Inafecta`, `IGV`, `Recargo`) de total final (`IMPORTE TOTAL`, `IMPORTE A PAGAR`, `I.T.`). No usa base como fallback de total.
- **Validador de consistencia contable (D-19, 2026-04-21)**: clasifica comprobante en `GRAVADA / EXONERADA / INAFECTA / MIXTA / NO_DETERMINABLE` y valida `total ≈ suma(componentes del tipo)` ±1.00. Estados: `OK / DIFERENCIA_LEVE / DIFERENCIA_CRITICA / DATOS_INSUFICIENTES`.

### Qué es parcial (cobertura dependiente de emisor)

- **`bi_gravado`**: prioridad `Valor Venta` / `V.V.` > `Op. Gravada` > `SUBTOTAL` > `Base Imponible`. Filtro anti-leyenda (`$`, `Sin impuestos`). Cobertura global 21/86 (24%) — residuales por ausencia estructural o decimales truncados por OCR.
- **`monto_igv`**: regex tolerante a OCR (`IGV | IGY | 15V | IBV | IOV`) + `Total I.G.V.` como fallback. Cobertura global 37/86 (43%).
- **`op_exonerada` / `op_inafecta`**: extracción línea por línea, acepta plural (`Exoneradas`, `Inafectas`), filtro anti-leyenda. Con cross-check que descarta valores > 1.5× total (fija columnas pegadas como `4160.00` → `None`).
- **`recargo_consumo`** (nuevo 2026-04-21): regex tolerante a OCR (`RECARGO AL CONSUMO`, `SERVICIO 10%`, `SERV1C1O`, `SERVCIO`, `SERVICE CHARGE`) con tolerancia O↔0, I↔1. 15 tests sintéticos pasando. Capacidad latente (0 casos en corpus actual — facturas de provincia no usan este renglón).
- **`clasificadores_gasto_expediente`** (nuevo 2026-04-21): extracción de códigos MEF `2.3.X Y.ZZ W` desde planilla/solicitud del expediente. Propagado a cada comprobante. Se capturan 4-5 clasificadores por expediente.

### Excel para validación humana (2026-04-21)

- **Archivo único**: `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (47 KB).
- **Export acumulativo por expediente**: al correr `python scripts/ingest_expedientes.py export` sin filtro se exportan los 4 expedientes; el upsert preserva columnas humanas ya llenas.
- **Hojas (orden de apertura)**:
  1. `resumen` — métricas ejecutivas, % por estado, desglose por expediente, instrucciones.
  2. `comprobantes` — 86 filas **ordenadas por prioridad**: CRITICA → INSUFICIENTES → LEVE → OK.
  3. `documentos`, `expedientes`, `errores`, `resolucion_ids` — hojas auxiliares.
- **Columnas nuevas (2026-04-21)** en hoja `comprobantes`:
  - `recargo_consumo` — extraído por regex tolerante a OCR.
  - `estado_consistencia` — `OK | DIFERENCIA_LEVE | DIFERENCIA_CRITICA | DATOS_INSUFICIENTES`.
  - `tipo_tributario` — `GRAVADA | EXONERADA | INAFECTA | MIXTA | NO_DETERMINABLE`.
  - `flag_revision_manual` — `SI` si el estado requiere revisión humana (70/86 = 81.4%).
  - `detalle_inconsistencia` — explicación textual auditable.
  - `clasificadores_gasto_expediente` — lista de códigos MEF del expediente.
  - `comentario_validacion` (humana) — para llenado libre durante revisión.

### Qué sigue inconsistente (residuales conocidos)

- **Marcoantonio (pp 30, 38, 46, 54 del 0316916)**: columnas ultra-compactas en tabla → Tesseract pega dígitos (`160` → `4160` / `460`). Filtro cross-check 1.5× descarta el valor contaminado pero no lo recupera. Requiere revisión manual contra PDF.
- **Boletas EB01 simplificadas**: el PDF imprime `OP.GRAVADA: 0.00 / EXONERADA: 0.00 / INAFECTA: 0.00` sin base real → clasificador las marca `DATOS_INSUFICIENTES` (honesto).
- **Restaurantes con decimales OCR-truncados (`S/ 80.0C`, `Si 4?.0;`)**: glifos rotos en imagen original, irrecuperables por preprocesamiento.
- **DIED-0250235**: OCR globalmente degradado → 24/29 son `DATOS_INSUFICIENTES`. Requiere reescaneo o validación manual completa.

### Transición del cuello de botella (2026-04-21)

Desde el baseline pre-SON (D-16, 2026-04-18) el cuello de botella ha evolucionado:

1. **Bottleneck histórico (pre-2026-04-18)**: OCR global (calidad de lectura página a página).
2. **Bottleneck intermedio (2026-04-18)**: interpretación semántica / parsing (jerarquía de anclas, filtros anti-leyenda). Atacado con SON, regex tolerantes, cross-check, validador tributario por tipo.
3. **Bottleneck actual (post-OCR-agresivo 2026-04-21)**: **layout / geometría / segmentación por regiones**. El OCR agresivo global ya alcanzó su techo (+4/59 recuperados = 6.8%). Los 55 casos residuales ya no son recuperables con más preprocesamiento de página completa; requieren:
   - lectura por BBoxes / ROI geométrico (columnas, celdas individuales), o
   - reconocimiento por plantilla del emisor (Marcoantonio vs Salchipapería vs SUNAT EB01), o
   - información física recuperable solo por reescaneo (decimales pixel-truncados).

**Decisión operativa**: no iterar más preprocesamiento OCR global. Ver D-22. Exploración de ROI geométrico queda como línea futura (ya documentada en D-11), condicionada al cierre de validación humana de esta fase.

---

### OCR agresivo como segunda pasada (2026-04-21)

- **Módulo**: `scripts/ingesta/ocr_region_totales.py`.
- **Estrategia**: render 500 DPI + 4 variantes preproc (soft / binary / deskew) × 2 PSM (6, 4) + mejor-de-N por longitud.
- **Hook**: `_cmd_process` llama `rellenar_desde_ocr_agresivo` solo para comprobantes con campos tributarios vacíos. NO sobrescribe valores ya capturados.
- **Resultado**: recuperó **4 de 59** `DATOS_INSUFICIENTES` (6.8%) — p56 (Transportes Rioja), p70/p78 (San Carlos), p94 (0344746). Los 55 restantes no son recuperables solo con preprocesamiento (límite de Tesseract en tablas densas + pixeles perdidos en escaneo).
- **Flag CLI**: `--skip-ocr-agresivo` para desactivar.

### Archivos del pipeline — última tocada

- `scripts/piloto_field_extract_paso4.py` — oráculo SON español→número, regex tolerantes OCR (IGV variantes, V.V., I.T., RECARGO/SERVICIO), cross-check físico 1.5×, cross-check suma informativo.
- `scripts/modelo/expediente.py` — `Comprobante.recargo_consumo` agregado.
- `scripts/consolidador.py` — propaga `recargo_consumo` al JSON.
- `scripts/ingesta/comprobante_extractor.py` — mapeo + función `rellenar_desde_ocr_agresivo`.
- `scripts/ingesta/ocr_region_totales.py` (NUEVO) — módulo OCR agresivo.
- `scripts/ingesta/excel_export.py` — columnas nuevas, sort por prioridad, hoja `resumen`.
- `scripts/ingest_expedientes.py` — `_clasificar_tipo_tributario`, `_evaluar_consistencia`, `_clasificadores_gasto_expediente`, parsing de tipo desde detalle, hook OCR agresivo.
- `scripts/document_ocr_runner.py` — preproc multi-pasada conservador-primero (de turno previo).

### PRE-PASO 4.5 — código preparado para `expediente.v4` (2026-04-27)

> Estado: **código mergeado, artefactos NO regenerados**. Las cifras de cobertura y el Excel de la sección anterior reflejan el estado v3 vigente. Esta sub-sección documenta solo qué se preparó a nivel de código.

- **Schema bump**: `scripts/modelo/expediente.py` — `SCHEMA_VERSION = "expediente.v4"`; 4 campos nuevos en `Comprobante`: `ruc_receptor`, `estado_consistencia`, `tipo_tributario`, `detalle_inconsistencia`.
- **Módulo puro nuevo**: `scripts/modelo/consistencia_tributaria.py` — extrae la lógica determinista (`clasificar_tipo_tributario`, `evaluar_consistencia`) que antes vivía en el exportador. Contrato: `evaluar_consistencia(...)` devuelve `(estado, tipo_tributario, detalle)`.
- **Propagación de `ruc_receptor`**: `scripts/ingesta/comprobante_extractor.py` — el campo ya extraído por PASO 4.1 ahora llega al `Comprobante` (antes se perdía en el filtro de kwargs).
- **Persistencia en consolidador**: `scripts/consolidador.py` — llama a `evaluar_consistencia` y rellena los 4 campos al construir cada `Comprobante`. La idempotencia byte-a-byte está cubierta por test sintético.
- **Exportador Excel adelgazado**: `scripts/ingest_expedientes.py` — borra `_clasificar_tipo_tributario` (33 líneas) y `_evaluar_consistencia` (134 líneas). Ahora **lee** `estado_consistencia` / `tipo_tributario` / `detalle_inconsistencia` desde el JSON. `flag_revision_manual` permanece en el exportador como lógica de presentación (qué fila pintar roja), no de modelo.
- **Tests sintéticos añadidos** (no tocan expedientes reales):
  - `tests/conftest.py` — inyecta `scripts/` en `sys.path`.
  - `tests/test_consistencia_tributaria.py` — 6 casos del módulo puro (gravada OK, leve, crítica, datos insuficientes ×2, exonerada).
  - `tests/test_consolidador_persistencia.py` — fixture sintético de 2 comprobantes verifica que los 4 campos lleguen al dataclass y al JSON serializado.
  - `tests/test_idempotencia_consolidador.py` — regla 6 de PASO 4.5: dos `consolidar()` consecutivos producen JSON byte-idéntico.
- **Lo que NO se hizo en esta fase** (deliberadamente, esperando autorización):
  - **No** se regeneró ningún `expediente.json` real. Los 4 expedientes en `control_previo/procesados/` siguen con `schema_version = "expediente.v3"` y sin los 4 campos nuevos.
  - **No** se regeneró el Excel. `validacion_expedientes.xlsx` sigue siendo el archivo v3 calculado por el código viejo del exportador.
  - **No** se ejecutó pipeline ni `run-all`.
- **Próximo paso autorizable**: regeneración controlada de 1 expediente piloto a v4 con verificación de que el Excel exportado preserva los mismos `estado_consistencia` / `tipo_tributario` que la versión v3 (no debe haber regresión semántica). Detalle en [`NEXT_STEP.md`](NEXT_STEP.md).
- **Decisión de respaldo**: D-24 en [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md).

### PASO 4.5 Fase 1 — motor determinista MVP (2026-04-28)

> Estado: **código mergeado en 4 commits, tests 69/69 verdes, motor NO ejecutado sobre expedientes reales todavía**. El piloto `DEBEDSAR2026-INT-0103251` ya está en formato `expediente.v4` (validado en PRE-PASO 4.5) y es el candidato para la primera ejecución autorizable; los otros 3 expedientes siguen en v3.

- **Schema de salida**: `decision_engine.v1` definido en `scripts/modelo/decision_engine_output.py` (dataclasses `DecisionEngineOutput`, `ResultadoRegla`, `Hallazgo`, `Criterio`, `MetadataCorrida`).
- **Estados**: `OK` / `OBSERVAR` / `REVISAR` / `NO_APLICABLE`. Principio: `OBSERVAR` = incumplimiento verificable; `REVISAR` = falta de evidencia para verificar.
- **Severidad opcional** (`BAJA` / `MEDIA` / `ALTA`) ortogonal al resultado, solo informa priorización; no entra en la agregación.
- **5 reglas MVP** registradas en `scripts/auditoria/reglas/`:
  - **R-IDENTIDAD-EXPEDIENTE** (scope=expediente): `BAJA_CONFIANZA` o conf<umbral → `REVISAR` (ajuste obligatorio: falta de certeza).
  - **R-CONSISTENCIA** (scope=comprobante): passthrough auditable de `estado_consistencia` ya calculado por el consolidador.
  - **R-CAMPO-CRITICO-NULL** (scope=comprobante): `monto_total` / `ruc` / `fecha` / `serie_numero` en null → `REVISAR` (con severidad ALTA o MEDIA según campo).
  - **R-FIRMAS** (scope=expediente): contra estados reales del módulo `validaciones/firmas_anexo3.py` — `CONFORME→OK`, `OBSERVADO→OBSERVAR`, `INSUFICIENTE_EVIDENCIA→REVISAR`, sin entrada → `NO_APLICABLE`.
  - **R-UE-RECEPTOR** (scope=comprobante): `ruc_receptor` == UE_ESPERADA → OK, ≠ → OBSERVAR, ausente → REVISAR. **`UE_ESPERADA="20380795907"` es valor temporal MVP** documentado como deuda en `scripts/auditoria/config.py`.
- **Agregación**: `decision_global = REVISAR` si cualquier regla es REVISAR; sino `OBSERVAR` si alguna; sino `OK`.
- **Orquestador**: `scripts/auditoria/decision_engine.py::evaluar_expediente(exp_dir)`. Solo lee, valida que el input sea `expediente.v4` (sino `SchemaVersionError`), calcula `expediente_json_sha256`, ejecuta las 5 reglas en orden estable, ordena hallazgos, retorna `DecisionEngineOutput`. **NO escribe `decision_engine_output.json` por sí sola**; el CLI solo escribe disco con flag `--out` explícito.
- **Idempotencia probada** (regla 6 PASO 4.5): dos llamadas consecutivas sobre el mismo input producen `to_dict_deterministic()` byte-idéntico. El sub-objeto `metadata_corrida` (timestamps + uuid + host + git_commit) está aislado y se excluye del diff.
- **Sin LLM**, sin re-OCR, sin re-extracción.
- **Tests añadidos en Fase 1** (todos sintéticos, sin tocar expedientes reales):
  - `tests/test_decision_engine_dataclasses.py` (7) — serialización determinista del schema.
  - `tests/test_reglas/test_r_*.py` (39 — uno por regla).
  - `tests/test_decision_engine_integracion.py` (9 — happy path + degradado).
  - `tests/test_decision_engine_idempotencia.py` (5 — regla 6 + estabilidad de hallazgos + sha256).
- **Resultado de suite global**: 69/69 PASSED en ~0.24 s.
- **Lo que NO se hizo en esta fase** (deliberadamente):
  - **No** se ejecutó el motor sobre ningún `expediente.json` real.
  - **No** se generó ningún `decision_engine_output.json`.
  - **No** se tocó Excel ni `expediente.json`.
  - **No** se integró con el flujo `ingest_expedientes.py` (subcomando `audit` queda para fase posterior).
- **Próximo paso autorizable**: ejecutar el motor sobre el piloto v4 ya validado. Detalle en [`NEXT_STEP.md`](NEXT_STEP.md).
- **Decisión de respaldo**: D-25 en [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md).

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

**Mapeo actual de los 4 expedientes** (al 2026-04-21):

| Expediente | Estado operativo |
|---|---|
| `DIED2026-INT-0250235` (piloto) | `pendiente_validacion_excel` — incluido en Excel consolidado |
| `DEBEDSAR2026-INT-0103251` (2do / robustez) | `pendiente_validacion_excel` — incluido en Excel consolidado |
| `DIED2026-INT-0344746` | `pendiente_validacion_excel` — incluido en Excel consolidado |
| `DEBE2026-INT-0316916` (nuevo 2026-04-21) | `pendiente_validacion_excel` — incluido en Excel consolidado |

**Todos los 4 expedientes están en Excel y esperan validación humana.**

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

## Política de versionado del Excel de validación (vigente desde 2026-04-21)

Regla operativa vinculante. Detalle formal en **D-23** de [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md).

1. **`data/piloto_ocr/metrics/validacion_expedientes.xlsx` es un artefacto de validación humana**, no la fuente técnica principal.
2. **La fuente de verdad técnica** es el JSON consolidado por expediente (`control_previo/procesados/<id>/expediente.json`) y la lógica determinista del pipeline. Ante discrepancia, manda el JSON. Ver D-13.
3. **El Excel NO se commitea automáticamente** durante iteraciones del pipeline. Se regenera libremente en disco local; no entra a Git por defecto.
4. **El Excel solo puede versionarse cuando Hans indique explícitamente** una frase equivalente a:
   - `EXCEL VALIDADO`
   - `AUTORIZADO PARA VERSIONAR`
5. Mientras el Excel esté en revisión o en estado provisional:
   - puede generarse y regenerarse con `python scripts/ingest_expedientes.py export`
   - puede usarse localmente para trabajo humano (rellenar columnas amarillas)
   - **NO debe entrar en `git add` / `git commit` / `git push`** salvo autorización explícita
6. Cuando Hans autorice versionar, el commit de evidencia debe describir **exactamente** qué expedientes y qué cobertura refleja (regla ya vigente del commit de evidencia).

**Estado actual del archivo:** está versionado en Git desde commits previos (evidencia incremental de turnos de trabajo). La regla anterior aplica **desde ahora hacia adelante**: no se agregará el `.xlsx` a nuevos commits sin autorización explícita. La opción de `git rm --cached` + migración a carpeta `artifacts/` queda como acción futura según D-17 / D-23.

### Protección operativa aplicada (2026-04-21)

Para que la regla sea efectiva sin requerir un commit ahora, se aplicaron **dos medidas locales**:

1. **`.gitignore`** — agregada entrada explícita para `data/piloto_ocr/metrics/validacion_expedientes.xlsx`. Queda activa el día que el archivo deje de estar trackeado (cuando Hans autorice `git rm --cached`).
2. **`git update-index --skip-worktree <path>`** — flag local aplicado sobre el archivo. Efecto inmediato: Git ignora cambios en el archivo en `git status`, `git add .`, `git commit -a`. El `.xlsx` **no puede entrar accidentalmente en commits** mientras esta bandera esté activa.

**Cómo se ve en `git ls-files -v`**: fila con prefijo `S` (skip-worktree).

### Cómo desproteger temporalmente para un commit autorizado

Cuando Hans autorice explícitamente versionar el Excel (frase equivalente a `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`), el procedimiento es:

```bash
# 1. Quitar skip-worktree para que Git vea el archivo modificado
git update-index --no-skip-worktree data/piloto_ocr/metrics/validacion_expedientes.xlsx

# 2. Stagear y commitear con mensaje describiendo expedientes y cobertura reflejada
git add data/piloto_ocr/metrics/validacion_expedientes.xlsx
git commit -m "evidence: Excel validado — <expedientes, estado, cobertura>"

# 3. Re-aplicar skip-worktree para que siga protegido después del commit
git update-index --skip-worktree data/piloto_ocr/metrics/validacion_expedientes.xlsx

# 4. (opcional) push
git push origin main
```

### Nota sobre otras copias / clones del repo

`skip-worktree` es **local a cada clone del repositorio**. Si Hans trabaja desde otra máquina o hace un clone nuevo, debe re-aplicar:

```bash
git update-index --skip-worktree data/piloto_ocr/metrics/validacion_expedientes.xlsx
```

Esta instrucción queda en D-23 del catálogo de decisiones.

---

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

*Última actualización: 2026-04-21 — 4to expediente (`DEBE2026-INT-0316916`) incorporado. Parsing determinista completado con oráculo SON en letras (+21 montos recuperados vs baseline), regex tolerantes OCR (IGV/V.V./I.T./RECARGO), cross-check físico 1.5×, cross-check suma. Validador refactorizado con jerarquía conceptual tributaria (GRAVADA/EXONERADA/INAFECTA/MIXTA) y estado_consistencia en 4 niveles. Excel final preparado con hoja `resumen`, orden por prioridad, columnas `tipo_tributario` / `flag_revision_manual` / `comentario_validacion`. OCR agresivo como 2da pasada implementado (recuperó 4/59 INSUFICIENTES). Agregadas decisiones D-18, D-19, D-20. **Fase abierta: pendiente validación humana del Excel** — ver [`NEXT_STEP.md`](NEXT_STEP.md).*

*Adenda 2026-04-27 — PRE-PASO 4.5: código preparado para `expediente.v4` (persistencia de `ruc_receptor` + `estado_consistencia` + `tipo_tributario` + `detalle_inconsistencia`). Lógica determinista movida del exportador al consolidador vía nuevo módulo puro `scripts/modelo/consistencia_tributaria.py`. Tests sintéticos añadidos (módulo puro, persistencia, idempotencia). **Artefactos reales (`expediente.json` y Excel) siguen en formato v3** — la regeneración controlada de 1 expediente piloto a v4 requiere autorización explícita. Decisión D-24 agregada.*

*Adenda 2026-04-28 — PASO 4.5 Fase 1: motor determinista MVP implementado (schema `decision_engine.v1`, 5 reglas atómicas, agregación por severidad máxima, idempotencia byte-a-byte probada). Sin LLM, sin re-OCR. Suite global 69/69 verde. Decisión D-25 agregada.*

---

## Cierre de sesión 2026-04-28

### Lo que se hizo hoy

- **PRE-PASO 4.5 cerrado** y commiteado en `eda3f4d` (schema `expediente.v4` con 4 campos persistidos: `ruc_receptor`, `estado_consistencia`, `tipo_tributario`, `detalle_inconsistencia`; lógica determinista movida a módulo puro nuevo `scripts/modelo/consistencia_tributaria.py`; exportador Excel adelgazado).
- **PASO 4.5 Fase 1 cerrado** y commiteado en `df813e2` (motor `scripts/auditoria/decision_engine.py` + 5 reglas atómicas + schema `decision_engine.v1` + tests sintéticos 60 nuevos, suite global 69/69 verde).
- **Piloto `DEBEDSAR2026-INT-0103251` regenerado localmente a `expediente.v4`** vía dos pasadas controladas:
  - 1ª: solo `consolidador.py` sobre `extractions/*.json` antiguos → `ruc_receptor` quedó `0/10` (los extractions previos no tenían el campo, esperable).
  - 2ª: `process` + `consolidate` con `--expediente-id` → `ruc_receptor` poblado en **9/10 comprobantes** con valor `20380795907` (RUC MINEDU). El 1/10 ausente coincide con el comprobante en `DATOS_INSUFICIENTES`.
- **Excel dedicado del piloto generado**: `data/piloto_ocr/metrics/validacion_DEBEDSAR2026-INT-0103251_v4_piloto.xlsx` — archivo separado vía flag `--xlsx` para no sobrescribir el consolidado. 10 filas, las 4 columnas `estado_consistencia` / `tipo_tributario` / `detalle_inconsistencia` / `flag_revision_manual` cuadran 1:1 con el JSON v4. **Excel principal `validacion_expedientes.xlsx` quedó intacto** (mtime 2026-04-21, sin cambios).
- **Motor 4.5 ejecutado sobre el piloto real** (primera corrida real fuera de fixtures sintéticos):
  - `decision_engine_output.json` generado en `control_previo/procesados/DEBEDSAR2026-INT-0103251/decision_engine_output.json` (10 729 B). Ruta gitignored, no se versiona.
  - `decision_global = REVISAR`. 9 hallazgos.
  - `expediente_json_sha256 = 2c6ff80e6af88043664e79f5695d773acb3b75f4b2c00bf7439794ed35c8ff43`.
- **Idempotencia empírica confirmada byte-a-byte**: 2ª corrida sobre el mismo input produjo payload determinista byte-idéntico (sha256 `b6f86ff35a…fb0ac9` en ambas), tamaño 10 729 B en ambas. `metadata_corrida` (run_id + timestamp) varía como diseñado.

### Estado actual del repo

- Código **PRE-PASO 4.5 commiteado en `main`** (`eda3f4d`). Sin push todavía.
- Código **PASO 4.5 Fase 1 commiteado en `main`** (`df813e2`). Sin push todavía.
- **Artefactos locales generados, NO versionados**:
  - Excel piloto v4 dedicado (`validacion_DEBEDSAR2026-INT-0103251_v4_piloto.xlsx`) → untracked en `data/piloto_ocr/metrics/`.
  - `decision_engine_output.json` del piloto → gitignored vía `control_previo/`.
  - Backups locales `.v3.bak.json`, `.v4.pre_reprocess.bak.json`, `extractions.v3.bak/` → gitignored vía `control_previo/`.
- Otros 3 expedientes (`DIED2026-INT-0250235`, `DIED2026-INT-0344746`, `DEBE2026-INT-0316916`) **siguen en `expediente.v3`** — el motor los rechazaría por `SchemaVersionError` si se intentara correr sobre ellos sin migración previa.
- Excel consolidado principal **sigue en estado previo** (4 expedientes en formato v3), no regenerado.
- **No existe aún exportador Excel del `decision_engine_output.json`** (visualización del veredicto del motor para revisor humano).
- **No existe aún capa IA conversacional** (que pueda explicar los hallazgos a jueces).

### Qué significa el resultado del piloto

- **`REVISAR` no es fallo del motor**. Significa que el motor, aplicando reglas deterministas sobre evidencia ya estructurada, encontró condiciones que requieren revisión humana: o bien evidencia insuficiente para certificar (ej. `ruc_receptor` ausente, identidad con `BAJA_CONFIANZA`), o bien diferencias contables no explicadas por los datos (ej. `bi_gravado` no extraído por OCR de tabla densa).
- **9 hallazgos del piloto, distribución por regla**:
  - `R-CAMPO-CRITICO-NULL = OK` — los 4 campos críticos (`monto_total`, `ruc`, `fecha`, `serie_numero`) están presentes en los 10 comprobantes.
  - `R-FIRMAS = OBSERVAR` — el Anexo 3 reporta `firmas_anexo3.estado=OBSERVADO` (algunos roles no detectados, no es ausencia total).
  - `R-CONSISTENCIA = REVISAR` — 5 comprobantes en `DIFERENCIA_CRITICA` (todos del patrón Marcoantonio con `bi_gravado` perdido por OCR de columnas pegadas, ya documentado en D-22) + 1 en `DATOS_INSUFICIENTES`.
  - `R-IDENTIDAD-EXPEDIENTE = REVISAR` — `BAJA_CONFIANZA` con conf=0.85 < umbral 0.9 (ajuste obligatorio Fase 1).
  - `R-UE-RECEPTOR = REVISAR` — 9/10 OK + 1/10 ausente (mismo comprobante que `DATOS_INSUFICIENTES`).
- **Cruce con realidad conocida del piloto**: las 4 hipótesis previas (decision_global=REVISAR, R-CONSISTENCIA con 5+1, R-UE-RECEPTOR 9/10, R-IDENTIDAD por BAJA_CONFIANZA) se confirmaron empíricamente. El motor produce las decisiones que el diseño anticipaba.
