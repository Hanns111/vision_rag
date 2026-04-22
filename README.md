# vision_rag

Sistema de análisis documental basado en RAG para normativa y, en paralelo, pipeline documental OCR (PASO 0–7).

---

## Estado actual del proyecto (Abril 2026)

> ⚠️ **Proyecto en validación humana activa. No es sistema de producción.**

### Fase en curso (NO cerrada)

El pipeline de ingesta + extracción + validación de comprobantes está **técnicamente estable**, pero la **fase de validación humana sigue ABIERTA**. La fase no se considera cerrada hasta que Hans revise manualmente el Excel generado contra los PDFs originales y emita decisión explícita de cierre.

### Pipeline funcional

- **Ingesta**: detecta y separa PDFs de planilla, solicitud, rendición, informe de comisión, anexos.
- **OCR**: Tesseract con preprocesamiento multi-pasada (baseline → enhanced → auto-rotate → aggressive, según calidad de página).
- **Parsing determinista** de comprobantes: RUC, razón social, serie, fecha, montos (`monto_total`, `bi_gravado`, `monto_igv`, `op_exonerada`, `op_inafecta`, `recargo_consumo`), clasificadores MEF del expediente.
- **Validador de consistencia contable**: clasifica cada comprobante por tipo tributario (`GRAVADA / EXONERADA / INAFECTA / MIXTA / NO_DETERMINABLE`) y marca `estado_consistencia` en cuatro niveles.
- **Export a Excel** ordenado por prioridad de revisión humana.

### Estado de procesamiento actual

- **4 expedientes procesados** (`DEBE2026-INT-0316916`, `DEBEDSAR2026-INT-0103251`, `DIED2026-INT-0250235`, `DIED2026-INT-0344746`).
- **86 comprobantes extraídos**, con estado distribuido: 15 `OK`, 1 `DIFERENCIA_LEVE`, 15 `DIFERENCIA_CRITICA`, 55 `DATOS_INSUFICIENTES`.
- **70 de 86 comprobantes (81.4%) con `flag_revision_manual = SI`**: requieren contraste humano contra PDF.

### Validación humana pendiente

El artefacto de revisión está en:

```
data/piloto_ocr/metrics/validacion_expedientes.xlsx
```

**La validación manual por parte de Hans aún no se ha realizado.** Por tanto:

- La fase permanece abierta.
- Los resultados del pipeline no se consideran verificados.
- Ningún uso productivo está autorizado sobre esta salida.

### Rol del Excel

- **Excel = artefacto de validación humana**, no fuente técnica principal (D-23).
- **Fuente de verdad técnica = JSON consolidado por expediente** en `control_previo/procesados/<id>/expediente.json` (D-13).
- El Excel se regenera libremente en disco local con `python scripts/ingest_expedientes.py export`; **no se versiona automáticamente en Git** (D-23, protección activa vía `.gitignore` + `git update-index --skip-worktree`).
- Solo se versiona cuando Hans autoriza explícitamente con frase equivalente a `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`.

### Entorno técnico real verificado

- **Sistema**: Windows 11, Git Bash (MINGW64).
- **Python**: 3.14.3 Windows nativo.
- **OCR**: Tesseract 5.4.0 **CPU-only**.
- **GPU**: RTX 5090 Laptop presente pero **no utilizada por el pipeline actual**; OpenCV compilado sin CUDA.
- **WSL/Linux nativo**: no activo.

Detalle en **D-21** (`docs/DECISIONES_TECNICAS.md`).

### Cuello de botella identificado (no resuelto)

Tras agotar mejoras de OCR global (preprocesamiento, multi-pasada, rasterización 500 DPI agresiva), el **siguiente cuello de botella** es **layout / geometría / segmentación** — columnas tributarias ultra-compactas en facturas tipo Marcoantonio, boletas EB01 simplificadas sin desglose real impreso, decimales truncados por escaneo degradado. No es atacable con más preprocesamiento; exploración de ROI geométrico / BBox queda como línea futura (D-11, D-22).

### Advertencia

- **Este sistema NO es producción.**
- Los resultados del pipeline dependen de validación humana antes de ser utilizables para control previo, auditoría o cualquier decisión operativa.
- No debe integrarse con AG-EVIDENCE ni con sistemas externos hasta cierre explícito de la fase de validación.

### Siguiente paso

Ver **[NEXT_STEP.md](NEXT_STEP.md)** — resumen: abrir Excel → leer hoja `resumen` → filtrar `flag_revision_manual=SI` → revisar primero `DIFERENCIA_CRITICA`, luego `DATOS_INSUFICIENTES` → completar columnas humanas → decisión explícita de cierre de fase.

---

## Qué hace

- Procesa documentos PDF (RAG en `agent_sandbox/`).
- Línea OCR separada: baseline en `scripts/document_ocr_runner.py` + piloto medible en `data/piloto_ocr/` (**ver `docs/ROADMAP_PROYECTO.md` §4.1–4.3**).
- Pipeline de ingesta de expedientes reales (`scripts/ingest_expedientes.py`) con extracción determinista de comprobantes y export a Excel de validación humana.

## Documentación

Documentación técnica viva: [CURRENT_STATE.md](CURRENT_STATE.md).  
Siguiente paso operativo: [NEXT_STEP.md](NEXT_STEP.md).  
Handoff Cursor: [CURSOR_HANDOFF.md](CURSOR_HANDOFF.md).  
**Roadmap ejecutable (PASO 0–7, N=15, bloqueos §5, checklist §9):** [docs/ROADMAP_PROYECTO.md](docs/ROADMAP_PROYECTO.md).  
**Poblar piloto OCR (raw, manifest, 15 labels):** [data/piloto_ocr/CHECKLIST_POBLADO.md](data/piloto_ocr/CHECKLIST_POBLADO.md).  
**Decisiones D-01 … D-23:** [docs/DECISIONES_TECNICAS.md](docs/DECISIONES_TECNICAS.md).  
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

1. **Validación humana del Excel** (prioridad actual — ver [NEXT_STEP.md](NEXT_STEP.md)). La fase **no se cerrará** hasta que Hans complete la revisión contra PDFs y emita decisión explícita.
2. Cerrar **PASO 0** (`docs/ROADMAP_PROYECTO.md` §9) — pendiente, bloqueado hasta definir criterio de aceptación tras validación humana.
3. **PASO 1** baseline y CSV en `data/piloto_ocr/metrics/` — pendiente.
4. Mejoras puntuales RAG según `CURRENT_STATE.md` cuando no compitan con la línea OCR / comprobantes.
