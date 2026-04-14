# vision_rag — Decisiones (tabla)

> Detalle de ruta: **[`ROADMAP_PROYECTO.md`](ROADMAP_PROYECTO.md)** (PASO 0–7, §4.1 cierre, §5 bloqueos, §9 checklist).

| ID | Decisión | Estado |
|----|----------|--------|
| D-01 | Rechazar VLM/LLM como OCR principal masivo | Cerrada |
| D-02 | Pipeline híbrido (preproceso → OCR → reglas → fallback LLM acotado) | Cerrada |
| D-03 | RAG en `agent_sandbox/` = consulta normativa con evidencia | Cerrada |
| D-04 | Docling / parsers cloud: solo tras bake-off (PASO 2) | Cerrada |
| D-05 | PaddleOCR: candidato; elección solo con métricas del piloto | Abierta hasta PASO 2 |
| D-06 | Baseline código: `scripts/document_ocr_runner.py` | Hecho |
| D-07 | Integración OCR ↔ agente: pendiente; **bloqueado** hasta PASO 7 por contrato | Pendiente |
| D-08 | PASO 0 v1 **documentado**: N=15, 11 campos, `piloto_ocr.v1`, rutas `data/piloto_ocr/` | Cerrada (documentación) |
| D-09 | **15 JSON** de etiquetas reales + `MANIFEST_PILOTO.csv` completo | Cerrada (piloto DEBEDSAR2026-INT-0103251; 2026-04-10) |
| D-10 | Validación obligatoria de **identidad única del expediente** (`EXPEDIENTE_ID` y reglas en [`GUARDARRAILES_AUDITORIA.md`](GUARDARRAILES_AUDITORIA.md)) antes de revisión documental o validación de gasto; sin ello **prohibido** declarar expediente válido | Cerrada (documentación) |
| D-11 | **OCR por regiones (ROI)** como **línea futura documentada** en [`ROADMAP_PROYECTO.md`](ROADMAP_PROYECTO.md) §11: sin número de PASO, sin implementación inmediata; exploración condicionada a métricas PASO 2–3 y trazabilidad por región | Documentada (no implementación) |

**Fuera de alcance inmediato:** GraphRAG sustitutivo sin evaluación; un solo proveedor OCR sin bake-off; tunear chunking RAG antes de baseline OCR en el piloto.

**Tras PASO 0 cerrado (D-09):** ejecutar PASO 1 y rellenar `metrics/baseline_*.csv`; luego PASO 2 y decisión D-05.
