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

---

## SIGUIENTE PASO (recomendado)

1. **Simplificar** `output_node`: respuesta más corta estilo asistente, opción de ocultar bloque “texto completo” o moverlo a modo verbose.
2. **Reducir longitud** por defecto del bloque principal y del listado de fragmentos secundarios.
3. **Mejorar UX** (variables de entorno, flags CLI, o UI ligera) según prioridad.
4. **Más adelante**: valorar integración con **AG-EVIDENCE** — **no** iniciar integración hasta cerrar estos puntos y acordar contrato de datos.

---

## REGLA IMPORTANTE

- **SANTO_GRIAL** = laboratorio / sandbox normativo (RAG + agente modular bajo `agent_sandbox/`).
- **AG-EVIDENCE** = línea de producto separada; **no** asumir enlaces de código ni despliegue compartido hasta decisión explícita.

---

## Referencia rápida de rutas

| Qué | Dónde |
|-----|--------|
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
- **`git push`:** no hay `remote` configurado en esta máquina. Cuando exista el remoto (p. ej. GitHub):

  ```bash
  git remote add origin <URL-del-repo>
  git push -u origin main
  ```

- En Windows, el repo usa `git config core.longpaths true` (evita fallos con rutas muy largas bajo `SANTO_GRIAL_ANALYSIS/`).

---

*Última actualización del documento: alineado con el cierre de sesión de trabajo (RAG normativo + agente + documentación).*
