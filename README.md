# vision_rag

Sistema de análisis documental basado en RAG para normativa y, en paralelo, pipeline documental OCR (PASO 0–7).

## Qué hace

- Procesa documentos PDF (RAG en `agent_sandbox/`).
- Línea OCR separada: baseline en `scripts/document_ocr_runner.py` + piloto medible en `data/piloto_ocr/` (**ver `docs/ROADMAP_PROYECTO.md` §4.1–4.3**).

## Estado

Documentación técnica viva: [CURRENT_STATE.md](CURRENT_STATE.md).  
Handoff Cursor: [CURSOR_HANDOFF.md](CURSOR_HANDOFF.md).  
**Roadmap ejecutable (PASO 0–7, N=15, bloqueos §5, checklist §9):** [docs/ROADMAP_PROYECTO.md](docs/ROADMAP_PROYECTO.md).  
**Decisiones:** [docs/DECISIONES_TECNICAS.md](docs/DECISIONES_TECNICAS.md).  
Taxonomía expedientes MINEDU: [docs/CONTROL_PREVIO_TAXONOMIA_EXPEDIENTES.md](docs/CONTROL_PREVIO_TAXONOMIA_EXPEDIENTES.md).  
Normativa por categoría: [control_previo/README.md](control_previo/README.md).

## Estructura

- `agent_sandbox/` — núcleo RAG + agente
- `scripts/` — OCR baseline, generadores de manifiesto
- `data/` — piloto OCR (`data/piloto_ocr/`); ver [data/README.md](data/README.md)
- `docs/` — roadmap, decisiones, estado RAG
- `control_previo/` — normativa y expedientes por categoría de negocio
- `tests/` — pruebas

## Próximos pasos

1. Cerrar **PASO 0** (`docs/ROADMAP_PROYECTO.md` §9).  
2. **PASO 1** baseline y CSV en `data/piloto_ocr/metrics/`.  
3. Mejoras puntuales RAG según `CURRENT_STATE.md` cuando no compitan con el piloto OCR.
