# Handoff para Cursor (al volver al proyecto)

**Propósito:** resumen estable para que el asistente y tú retomen el hilo **sin depender del chat anterior**. El detalle técnico del RAG sigue en `CURRENT_STATE.md`.

---

## Raíz del workspace

`C:\Users\Hans\Proyectos\vision-rag`

Todo lo demás es relativo a esta carpeta salvo que se indique lo contrario.

---

## Qué es este repo (dos piezas distintas)

1. **SANTO GRIAL — RAG normativo + agente (núcleo)**  
   - Carpeta: `agent_sandbox/`  
   - PDF → texto con **PyMuPDF**, chunks, embeddings, índice JSON, búsqueda híbrida.  
   - Orquestación: `orchestrator.py` — ciclo razonamiento → herramienta (`buscar_en_pdf`) → validación (máx. 2 vueltas).  
   - Entrada: `agent_sandbox/main.py` (también eval RAG con `--rag-eval`).  
   - **Estado detallado, limitaciones y rutas:** leer **`CURRENT_STATE.md`**.

2. **OCR ligero (auxiliar, no integrado al agente)**  
   - Script: `scripts/document_ocr_runner.py`  
   - Flujo: si la página PDF tiene bastante texto incrustado → usa capa digital; si no → raster + OpenCV (CLAHE) + **Tesseract**.  
   - Dependencias: `scripts/requirements-ocr.txt` + binario **Tesseract** en el sistema.  
   - **No** forma parte del pipeline RAG principal; es herramienta aparte para carpetas de PDFs escaneados.

---

## Qué NO es el grueso del repo

- No hay un pipeline CV multi-agente integrado en Python en todo el monorepo.  
- Volumen grande (GB) en disco suele ser **PDFs y carpetas documentales**, no solo código.  
- Hay código TypeScript de referencia (`output/`, `SANTO_GRIAL_ANALYSIS/`) orientado a IDE/clipboard; **no** sustituye al flujo `agent_sandbox`.

---

## Sesiones recientes (contexto humano)

- Se documentó el repo con un **análisis estructurado (PROMPT 1):** sistema principal = RAG + agente; OCR = script aislado.  
- Se acordó: **la memoria del chat no sustituye** notas en archivos; este handoff + `CURRENT_STATE.md` son la fuente de verdad.

---

## Cómo usar esto en Cursor

- Escribir en el chat: *«Lee `CURSOR_HANDOFF.md` y `CURRENT_STATE.md`»* al abrir el proyecto.  
- O `@CURSOR_HANDOFF.md` al hacer una pregunta.

---

## Siguiente paso sugerido (opcional)

- Integrar o no el OCR con el RAG (decisión de producto).  
- Si se busca pipeline multi-agente CV/OCR, diseñarlo **aparte** o como nuevo paquete bajo `agent_sandbox/` o `scripts/` con contratos claros.

---

*Creado para continuidad entre sesiones; actualizar este archivo cuando cambie el alcance o la arquitectura.*
