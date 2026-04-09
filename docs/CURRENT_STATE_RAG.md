# Estado actual del RAG normativo (snapshot)

> **Nota:** Este documento describe un **punto intermedio de depuración estructural**, no un estado final de producción.

**Última actualización:** 2026-04-08  
**Versión de índice:** `INDEX_SCHEMA_VERSION = 4` (`index/index.json`)

---

## 1. Arquitectura actual (resumen)

| Capa | Descripción |
|------|-------------|
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2`; vectores por chunk; sin cambios de modelo en la iteración reciente. |
| **Recuperación** | Coseno query–chunk + score híbrido (semántica + keywords + ajustes por tipo de chunk + intención léxica). |
| **Pool multivista** | Pool fijo **10**: ~6 mejores por score híbrido global + hasta 2 por señal léxica + hasta 2 por señal estructural; unión, deduplicación y rerank local. |
| **Rerank** | Re-ranking local heurístico sobre el pool; opcionalmente **cross-encoder** BGE (`max_length=1024`) si hay CUDA; si no, torneo pairwise. |
| **Salida** | Top-10 al caller; interfaces públicas principales sin rediseño. |

**Código principal:** `agent_sandbox/pdf_rag.py`, `agent_sandbox/cross_encoder_rerank.py`, `agent_sandbox/main.py` (benchmark).

---

## 2. Cambios implementados en la iteración reciente

### Multi-view retrieval

- Constantes: `K_POOL_SEMANTIC=6`, `K_POOL_LEX=2`, `K_POOL_STRUCT=2`, `TOP_K_POOL=10`.
- Funciones: `recuperar_lexico`, `recuperar_estructural`, `_merge_pool_multivista`.
- Objetivo: mejorar recall sin subir K global; combinar señales semánticas, léxicas y estructurales.

### Cross-encoder

- Modelo: `BAAI/bge-reranker-v2-m3`.
- `max_length=1024` (antes 512) para reducir truncamiento con contexto local (vecinos).

### Nuevo chunking (schema 4)

- **Cortes** al detectar encabezados normativos (OBJETIVO, secciones numeradas, artículo, numeral, anexo en cuerpo) usando `cortar_chunk_antes_siguiente_palabra` sobre el stream de palabras.
- **Encabezados en dos líneas (parcial):** estado `sec_linea_num_pendiente` — si una línea es solo numeración de al menos dos niveles (p. ej. `6.4.`) y la siguiente es el título, se fusionan antes de aplicar `_es_encabezado_seccion`. Restricciones para no confundir con TOC (`1.`) ni números sueltos.
- **Anexos:** el corte fuerte de tipo anexo se omite solo en **TOC** (`in_toc_block` o línea con puntos guía tipo `_es_entrada_toc`), para limitar micro-chunks en el índice.
- **Títulos:** filtros de “basura” (firmas, tablas, entradas tipo índice); umbral relajado para mayúsculas tipo título (`len >= 20`) con exclusiones TOC/anexo índice.
- **Índice:** `INDEX_SCHEMA_VERSION = 4` fuerza reconstrucción si el JSON en disco es de versión anterior.

---

## 3. Resultado del benchmark actual

- **Medido en entorno de desarrollo (pairwise, sin GPU CE en muchas corridas):** **12/18** aciertos top-1 (archivo **y** página dentro de tolerancia).
- **Contexto:** Hubo **16/18** en configuraciones anteriores (chunking/pool distintos); la migración a chunking v4 y el nuevo mapa de chunks produjo **regresión** en la métrica agregada.

---

## 4. Diagnóstico técnico: ítems #2, #4, #8

| Ítem | Pregunta (idea) | Observación |
|------|-------------------|-------------|
| **#2** | Ámbito / “a quiénes aplica” | El gold suele estar relacionado con **sección 2 (ÁMBITO)** frente a **OBJETIVO** y **BASE NORMATIVA**. En páginas iniciales, **portada + índice** pueden compartir chunk; el cuerpo en p.~4 puede seguir mezclando ruido de estructura si el PDF no alinea cortes con secciones reales. El **ranking** puede acertar archivo y fallar página o fragmento. |
| **#4** | Plazo / rendición (comisionado) | Gold en torno a **6.4.x**; el numeral **6.4.2** puede quedar **partido** entre chunks o competir con otro fragmento (p. ej. 6.4.x vs 6.5 o responsabilidades). |
| **#8** | Reprogramaciones de otorgamiento | La sección **6.5** existe en chunks con título coherente en algunos casos; el fallo suele ser **orden top-1** (otro chunk gana por score híbrido / pairwise / CE) más que ausencia total del texto. |

Estos puntos deben validarse siempre con **mismo índice** y, si aplica, **CE en GPU**.

---

## 5. Problemas estructurales identificados

1. **Encabezados en dos líneas:** la heurística actual exige **dos niveles** (`6.4`) y no equivocarse con TOC; los PDFs pueden partir títulos de forma distinta (espacios, guiones, mayúsculas), por lo que la detección sigue siendo **parcial**.
2. **Chunking en secciones 6.x:** los límites no siempre coinciden con subnumeraciones reales (**6.4.2** puede quedar en el límite de dos chunks).
3. **Anexos:** tensiones entre **evitar explosión** de chunks de 5–20 palabras y **mantener cortes** útiles en cuerpo; líneas tipo “ANEXO N° …” en índice vs cuerpo requieren reglas finas.
4. **Títulos:** riesgo de **vacío**, **engaño** (línea de índice como título de chunk grande) o **inconsistencia** entre `titulo` y contenido principal del chunk.
5. **Contaminación caso #2:** mezcla conceptual **OBJETIVO + ÁMBITO + BASE NORMATIVA** cuando el **bloque índice/cubierta** sigue en el mismo chunk que referencias a esas secciones, o cuando el chunk de cuerpo no separa 1 / 2 / 3 como en el PDF impreso.

---

## 6. Conclusión

**El cuello de botella actual es principalmente estructural (chunking y alineación con el PDF), no la calidad intrínseca del modelo de embeddings ni del cross-encoder como única causa.**

Mejorar solo ranking o pesos sin ajustar **dónde corta** el texto seguirá dejando techo bajo en casos donde la respuesta es una **frase fina** dentro de un chunk largo o partida.

---

## NEXT STEP (CRÍTICO)

### Estrategia obligatoria

- **Iteración controlada:** como mucho **un cambio estructural por ciclo** (chunking, regex de encabezado, regla de anexo, umbral de título, etc.).
- Tras cada cambio:
  1. **Reconstruir índice** (borrar o invalidar `index/index.json` si cambia schema o lógica de chunks).
  2. **Correr benchmark:** `python main.py --rag-eval-benchmark` (idealmente con CE en GPU para comparar con producción).
  3. **Analizar siempre** los casos **#2, #4, #8** (top-3, archivo, página, `titulo`, `score` / `score_rerank`).

### Próximo objetivo técnico (orden sugerido)

1. **Corregir y validar** la detección de encabezados en **dos líneas** (p. ej. `6.4.` + título en la siguiente), con pruebas sobre líneas reales extraídas del PDF.
2. **Alinear** cortes de chunk con la **estructura real** del documento (secciones 1–9 y 6.x), minimizando mezcla índice/cuerpo.
3. **Reducir chunks basura** en anexos sin perder cortes necesarios en el cuerpo normativo.

### No hacer en el mismo ciclo

- Cambiar modelo de embeddings, rehacer todo el pipeline o acumular varias heurísticas sin medir entre medias.

---

## Referencias rápidas

| Recurso | Ruta |
|---------|------|
| Benchmark | `agent_sandbox/eval_questions.json` |
| Índice | `agent_sandbox/index/index.json` (o `AGENT_INDEX_JSON`) |
| Corpus | `agent_sandbox/corpus/` |
| Changelog | `docs/CHANGELOG.md` |
