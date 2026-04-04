# Paquete para auditoría — sandbox (reconstruido / actualizado 3 abr. 2026)

Este directorio es una **copia de conveniencia** del código y documentación de **tu** `agent_sandbox`: sirve para que un LM revise arquitectura y te ayude a **endurecer o alinear** tu **proyecto de evidencia**, siempre reinterpretando recomendaciones (no es el árbol de referencia “Claude” en sí; es **tu** código).

El **análisis grande** (miles de archivos TS/TSX reconstruidos, blueprints, índice) está en **`../../../SANTO_GRIAL_ANALYSIS/`** (sube tres niveles desde esta carpeta hasta la raíz `SANTO GRIAL`). Puerta de entrada ordenada: **`../README.md`**, **`../INDICE_MAESTRO.md`**, **`../CLAVES_REINGENIERIA_SINTESIS.md`**.

No es obligatorio llamarlo “código fuente” en el chat con el auditor: puede describirse como *snapshot del sandbox para revisión*.

## Cómo usarlo con ChatGPT

1. **Opción A — Zip:** comprime toda la carpeta `AGENT_SANDBOX_SOURCE_FOR_AUDIT` y súbela al chat (si tu plan lo permite).
2. **Opción B — Pegar:** abre cada archivo en este orden sugerido y pégalo en el chat con encabezado `### archivo: nombre.py`:
   - `ARCHITECTURE.md`, `README.md`, `requirements.txt`
   - `pdf_rag.py`, `embeddings.py`, `tools.py`, `orchestrator.py`, `state.py`
   - `main.py`, `llm_client.py`, `agent_audit_log.py`
   - `nodes/input_node.py`, `nodes/reasoning_node.py`, `nodes/tool_node.py`, `nodes/validation_node.py`, `nodes/output_node.py`, `nodes/__init__.py`

3. **Instrucción sugerida al auditor:**  
   *“Auditoría de arquitectura y riesgos: no ejecutar; revisar diseño, acoplamiento, RAG/chunking y separación de responsabilades.”*

## Qué **no** está aquí (y por qué)

- No se incluyen `corpus/`, `index/`, `logs/`, PDFs ni datos.
- Copias locales pueden quedar **desactualizadas** si cambias el código en `agent_sandbox/`; vuelve a copiar antes de una nueva auditoría si hace falta.
