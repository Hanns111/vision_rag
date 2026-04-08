# vision_rag

Sistema de análisis documental basado en RAG para normativa.

## Qué hace

- Procesa documentos PDF
- Extrae texto (OCR si necesario)
- Indexa contenido
- Permite consultas con trazabilidad

## Estado

Proyecto en desarrollo – fase de optimización de retrieval y ranking.

Documentación técnica viva: [CURRENT_STATE.md](CURRENT_STATE.md).  
Contexto para retomar el trabajo en Cursor: [CURSOR_HANDOFF.md](CURSOR_HANDOFF.md).

## Estructura

- `agent_sandbox/` — núcleo RAG + agente
- `scripts/` — utilidades (p. ej. OCR)
- `data/` — datos locales (contenido no versionado; ver `data/README.md`)
- `docs/` — documentación adicional
- `tests/` — pruebas

## Próximos pasos

- Evaluación benchmark
- Mejora de ranking
- Motor de reglas
