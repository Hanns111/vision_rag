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

*Última actualización: 2026-04-14 — PASO 4.1 cerrado; gobernanza operativa documentada.*
