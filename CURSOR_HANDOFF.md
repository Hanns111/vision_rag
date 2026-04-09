# Handoff para Cursor (al volver al proyecto)

**Propósito:** retomar el hilo sin el chat. Detalle RAG: `CURRENT_STATE.md`.  
**Roadmap (PASO 0–7):** [`docs/ROADMAP_PROYECTO.md`](docs/ROADMAP_PROYECTO.md) · **PASO 0** (N=15, §4.1–4.3, checklist §9): `data/piloto_ocr/README.md`  
**Decisiones:** [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md) (D-09 = etiquetado pendiente)  
**Normativa / expedientes por categoría:** [`control_previo/README.md`](control_previo/README.md) · manifiestos: `control_previo/MANIFEST_INGESTION_TODO.csv` (regenerar con `python scripts/gen_control_previo_manifests.py`).

---

## Raíz del workspace

`C:\Users\Hans\Proyectos\vision_rag`

Todo lo demás es relativo a esta carpeta salvo que se indique lo contrario.

---

## Qué es este repo (dos piezas distintas)

1. **Núcleo RAG normativo + agente (`agent_sandbox/`)**  
   - PDF → texto con **PyMuPDF**, chunks, embeddings, índice JSON, búsqueda híbrida.  
   - Orquestación: `orchestrator.py` — ciclo razonamiento → herramienta (`buscar_en_pdf`) → validación (máx. 2 vueltas).  
   - Entrada: `agent_sandbox/main.py` (también eval RAG con `--rag-eval`).  
   - **Estado:** `CURRENT_STATE.md`.

2. **OCR / piloto documental (PASO 0–2)**  
   - Script baseline: `scripts/document_ocr_runner.py` (PyMuPDF + OpenCV + Tesseract).  
   - **Ground truth y métricas:** `data/piloto_ocr/` según roadmap §4.1–4.3. **No** integrado al agente hasta PASO 7 (D-07).

---

## Qué NO es el grueso del repo

- No hay pipeline CV multi-agente integrado en un solo ejecutable Python.  
- Volumen grande en disco: PDFs y carpetas documentales.  
- Material opcional en `output/` (gitignore). `SANTO_GRIAL_ANALYSIS/` retirada del árbol local si existía.

---

## Cómo usar esto en Cursor

- *«Lee `CURSOR_HANDOFF.md` y `CURRENT_STATE.md`»* al abrir el proyecto.

---

## Orden sugerido (roadmap)

1. Completar **§9** en `docs/ROADMAP_PROYECTO.md` (PASO 0).  
2. **PASO 1** baseline → `data/piloto_ocr/metrics/`.  
3. **PASO 2** bake-off. Integración OCR ↔ agente solo con contrato (**PASO 7**, D-07).

---

*Actualizar cuando cambie alcance o arquitectura.*
