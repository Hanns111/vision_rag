# LLM_HANDOFF_MASTER — Contexto maestro para cualquier LLM

> Cualquier LLM que lea este documento debe tener una imagen completa del proyecto, su estado, su estrategia y cómo retomarlo sin contexto previo.

**Proyecto:** vision_rag
**Repo:** Hanns111/vision_rag
**Ruta local:** `C:\Users\Hans\Proyectos\vision_rag`
**Rama:** `main`
**Fecha de cierre:** 2026-04-14

---

## 1. Proposito del proyecto

Sistema de procesamiento documental para expedientes de pago del sector publico peruano (MINEDU). Dos piezas independientes:

1. **RAG normativo** (`agent_sandbox/`) — operativo. Responde preguntas sobre directivas con evidencia trazable. No depende del pipeline OCR.
2. **Pipeline OCR/extraccion** (PASO 0-7) — en construccion. Extrae campos estructurados (RUC, montos, fechas, serie/numero) de facturas, recibos y documentos escaneados.

Las dos piezas no se integran hasta PASO 7 (decision D-07).

---

## 2. Estado actual del roadmap

**PASO 0 a 4.1: completados y estables.**
**PASO 5: NO iniciado. NO es prioridad inmediata.**

| PASO | Estado | Commit | Que se hizo |
|------|--------|--------|-------------|
| 0 | Cerrado | `54517f7` | 15 paginas etiquetadas, manifest, ground truth |
| 1 | Cerrado | `3f2a5cc` | Baseline Tesseract sobre piloto |
| 2 | Cerrado | `fc31b7f` | Bake-off: Tesseract vs PaddleOCR vs Docling en WSL |
| 3 | Cerrado | `9ad4e8f` | Mini A/B preproceso: sin mejora, no iterar |
| 4 | Cerrado | `d67e01b` | Extractor por reglas: +21 vs minimal, 0 regresiones |
| 4.1 | Cerrado | `734bb5c` | Correccion: +33 vs minimal, 0 regresiones |
| 5 | No abierto | — | Fallback LLM — pendiente, no prioridad |
| 6 | Prototipo | — | RAG en agent_sandbox/, independiente |
| 7 | Bloqueado | — | Integracion OCR + agente; requiere contrato de datos |

---

## 3. Resumen por fases

**PASO 0 — Dataset piloto**
- 15 paginas de un expediente real (DEBEDSAR2026-INT-0103251)
- 3 PDFs: recibo ingreso, solicitud/planilla viaticos, rendicion con facturas
- 11 campos por pagina, esquema `piloto_ocr.v1`
- Ground truth manual en `data/piloto_ocr/labels/`

**PASO 1 — Baseline OCR**
- Tesseract + PyMuPDF sobre las 15 paginas
- Metricas en `data/piloto_ocr/metrics/baseline_paso1_20260410.csv`
- Establece el piso contra el que se compara todo lo demas

**PASO 2 — Bake-off motores**
- Tesseract vs PaddleOCR vs Docling
- PaddleOCR solo viable en WSL/Linux (fallo en Windows por oneDNN)
- Tesseract gano en F1; Docling mas lento sin mejora
- Decision D-12: WSL es entorno preferente

**PASO 3 — Descartado**
- Mini A/B con CLAHE y unsharp mask sobre 3 paginas
- 0 mejora en campos objetivo
- Conclusion: el cuello de botella no es preproceso, es parsing

**PASO 4 — Parsing con reglas**
- Extractor determinista `scripts/piloto_field_extract_paso4.py`
- 8 tipos documentales reconocidos
- Traza JSON por campo: tipo_doc, regla, lineas_usadas
- +21 aciertos vs minimal, 0 regresiones

**PASO 4.1 — Estabilizacion**
- Correccion de 4 regresiones en monto_subtotal (regex "Sub Total Ventas")
- Mejora razon_social_emisor: 0/10 a 8/10
- Resultado final: +33 vs minimal, 0 regresiones
- Este es el estado actual del sistema

---

## 4. Resultado clave

El cuello de botella paso de OCR a parsing. El sistema ahora extrae correctamente:

| Campo | Aciertos / Evaluables |
|-------|-----------------------|
| tipo_documento | 15/15 (100%) |
| serie_numero | 13/13 (100%) |
| monto_subtotal | 9/9 (100%) |
| monto_total | 12/12 (100%) |
| monto_igv | 9/9 (100%) |
| fecha_emision | 14/14 (100%) |
| ruc_receptor | 9/9 (100%) |
| ruc_emisor | 10/13 (77%) |
| razon_social_emisor | 8/10 (80%) |
| moneda | 12/13 (92%) |

**Todo sin LLM. Todo determinista. Todo trazable.**

---

## 5. Artefactos importantes (con rutas)

| Artefacto | Ruta |
|-----------|------|
| Ground truth (15 JSON) | `data/piloto_ocr/labels/*.json` |
| Manifest piloto | `data/piloto_ocr/MANIFEST_PILOTO.csv` |
| PDFs raw del piloto | `data/piloto_ocr/raw/` |
| Baseline PASO 1 | `data/piloto_ocr/metrics/baseline_paso1_20260410.csv` |
| Bake-off PASO 2 (WSL) | `data/piloto_ocr/metrics/bakeoff_paso2_consolidado_20260414_linux_wsl.csv` |
| Textos OCR por motor | `data/piloto_ocr/metrics/paso2_linux_wsl/tesseract_baseline/*.txt` |
| PASO 3 A/B resultados | `data/piloto_ocr/metrics/paso3_ab_linux_wsl/` |
| PASO 4 eval (pre-4.1) | `data/piloto_ocr/metrics/paso4_eval_linux_wsl/*_pre41.*` |
| PASO 4.1 eval (final) | `data/piloto_ocr/metrics/paso4_eval_linux_wsl/paso4_eval_detalle_20260414.csv` |
| Trazas JSON PASO 4.1 | `data/piloto_ocr/metrics/paso4_eval_linux_wsl/paso4_eval_trazas_20260414.json` |
| Informe PASO 4.1 | `data/piloto_ocr/metrics/paso4_eval_linux_wsl/INFORME_PASO4_EVAL_20260414.md` |
| Extractor reglas | `scripts/piloto_field_extract_paso4.py` |
| Script eval | `scripts/piloto_paso4_eval.py` |
| Script baseline OCR | `scripts/document_ocr_runner.py` |
| Metricas minimas | `data/piloto_ocr/metrics/METRICAS_MINIMAS.md` |

---

## 6. Decisiones tecnicas (D-01 a D-12)

| ID | Decision | Estado |
|----|----------|--------|
| D-01 | Rechazar VLM/LLM como OCR principal masivo | Cerrada |
| D-02 | Pipeline hibrido: preproceso -> OCR -> reglas -> fallback LLM acotado | Cerrada |
| D-03 | RAG = capa posterior, no sustituto de extraccion | Cerrada |
| D-04 | Docling/parsers cloud: solo tras bake-off | Cerrada |
| D-05 | PaddleOCR: candidato, sin decision sin metricas | Abierta |
| D-06 | Baseline: `scripts/document_ocr_runner.py` | Hecho |
| D-07 | Integracion OCR <-> agente: bloqueado hasta PASO 7 | Pendiente |
| D-08 | PASO 0 documentado: N=15, 11 campos, piloto_ocr.v1 | Cerrada |
| D-09 | 15 etiquetas + manifest completo | Cerrada |
| D-10 | Validacion identidad expediente obligatoria antes de declarar valido | Cerrada |
| D-11 | OCR por regiones (ROI): linea futura, sin PASO asignado | Documentada |
| D-12 | Entorno preferente: Linux/WSL para OCR avanzado y bake-off | Cerrada |

---

## 7. Guardarrailes

- **Identidad del expediente:** antes de validar cualquier gasto, verificar que el EXPEDIENTE_ID es unico y coherente. Sin esto, prohibido declarar expediente valido (D-10).
- **Coherencia documental:** manifest debe coincidir con raw/ y labels/. Suma de paginas_en_piloto = 15.
- **Validacion cruzada:** monto_total = monto_subtotal + monto_igv (donde aplique). Si no cuadra, marcar `requiere_revision: true`.
- **Trazabilidad:** cada campo extraido tiene traza (regla, lineas_usadas, tipo_doc). Sin traza = no confiable.
- **Sin alucinaciones:** el extractor devuelve `null` si no encuentra un campo. Nunca inventa valores.

---

## 8. Roles operativos

| Rol | Quien | Alcance |
|-----|-------|---------|
| **Decisor final** | Hans | Aprueba fases, cambios de rumbo, push a remoto |
| **Ejecutor principal** | Claude Code | Modifica archivos, commit, push — bajo decision de Hans |
| **Apoyo secundario** | Cursor | Ejecucion/documentacion cuando Hans lo convoque |
| **Auditor / continuidad** | ChatGPT | Control de fase, consistencia entre herramientas |

---

## 9. Que NO hacer

1. **No introducir LLM** para extraccion sin justificacion cuantitativa y aprobacion de Hans.
2. **No romper el determinismo.** El sistema es auditable porque no tiene componentes estocasticos.
3. **No mezclar subvencion** (`06_subvenciones` excluida del piloto).
4. **No tocar** `orchestrator.py` ni `agent_sandbox/` (linea RAG separada).
5. **No integrar OCR al agente** hasta PASO 7 con contrato de datos (D-07).
6. **No reabrir roadmap** ni arquitectura sin datos nuevos que lo justifiquen.
7. **No proponer GraphRAG, long context, ni cambios de modelo** sin cerrar primero la linea OCR.
8. **No hacer push sin aprobacion de Hans.**

---

## 10. Estrategia actual del sistema (CRITICO)

### El enfoque es determinista, no basado en LLM

Esto no es una limitacion. Es la decision de diseno central del proyecto.

**Por que:**
- Velocidad: milisegundos por pagina vs segundos con LLM
- Auditabilidad: traza completa por campo (regla + lineas)
- Reproducibilidad: misma entrada = misma salida, siempre
- Costo: corre con Tesseract en cualquier maquina, sin GPU ni API
- Sin alucinaciones: null antes que inventar

**Evidencia:** PASO 4.1 logro +33 aciertos sobre 150 campos evaluados, 0 regresiones, sin ninguna llamada a LLM.

**LLM como fallback futuro (PASO 5):**
- Esta considerado en el roadmap
- NO esta activado
- NO es prioridad inmediata
- Solo se evaluaria tras validar generalizacion en expedientes nuevos
- Requiere techo de llamadas, log obligatorio y justificacion cuantitativa

**Riesgos de introducir LLM antes de tiempo:**
- Enmascara debilidades del OCR/parsing que deben resolverse con reglas
- Introduce latencia y costo sin evidencia de retorno
- Dificulta auditoria (caja negra vs traza determinista)
- Crea dependencia de API/GPU que el sistema actual no tiene
- 43% de fallos restantes son OCR_NO_PRESENTE: LLM sobre texto no los resuelve

---

## 11. Problemas abiertos

| Tipo | Cantidad | Paginas | Solucionable con reglas | Solucionable con LLM texto |
|------|----------|---------|------------------------|---------------------------|
| OCR_NO_PRESENTE (ruc_emisor) | 3 | p5, sol-p1, sol-p2 | No | No |
| OCR_AMBIGUO (razon_social) | 1 | sol-p2 | Riesgo alto | Parcialmente |
| Layout fragmentado (razon_social) | 1 | p19 | Dificil | Parcialmente |
| Sin senal OCR (moneda) | 1 | sol-p1 | No | No |
| Total fallos | 6 de 150 campos | — | — | — |

**Nota:** 4 de 6 fallos NO se resuelven con LLM sobre texto. Solo 2 son candidatos parciales.

---

## 12. Siguiente paso logico

**NO es PASO 5 (LLM). Es validacion en mas expedientes reales.**

El pipeline se construyo y evaluo sobre un solo expediente (DEBEDSAR2026-INT-0103251, 15 paginas). Antes de anadir complejidad:

1. Seleccionar un segundo expediente de viaticos (diferente proveedor, diferente UE).
2. Etiquetar 10-15 paginas nuevas con esquema `piloto_ocr.v1`.
3. Correr el extractor PASO 4.1 sin modificar y medir.
4. Analizar fallos: si son reglas nuevas o limitaciones estructurales.

Si generaliza: el pipeline esta listo para escalar sin LLM.
Si no generaliza: los datos de fallo dicen que ajustar.

---

## 13. Como retomar el proyecto

### Lectura minima obligatoria
1. Este archivo (`LLM_HANDOFF_MASTER.md`)
2. `CURRENT_STATE.md` (estado vivo + gobernanza)
3. `docs/ROADMAP_PROYECTO.md` (roadmap completo, S4.1-4.3, S9)

### Verificacion rapida
```bash
cd C:\Users\Hans\Proyectos\vision_rag
git log --oneline -10
# Confirmar que el ultimo commit es el cierre de sesion
```

### Ejecutar evaluacion existente
```bash
cd C:\Users\Hans\Proyectos\vision_rag
PYTHONPATH=scripts python scripts/piloto_paso4_eval.py
# Debe producir INFORME en data/piloto_ocr/metrics/paso4_eval_linux_wsl/
# Verificar: mejoras netas = 33, regresiones = 0
```

### Estructura del repo
```
vision_rag/
  agent_sandbox/          # RAG normativo + agente (independiente)
  scripts/                # OCR baseline, extractor PASO 4, eval, engine adaptativo
  data/piloto_ocr/        # Piloto: raw/, labels/, metrics/, manifest
  docs/                   # Roadmap, decisiones, estado RAG, taxonomia
  control_previo/         # Normativa y expedientes MINEDU (local, no en git)
  tests/
```

### Archivos clave
| Archivo | Que contiene |
|---------|-------------|
| `LLM_HANDOFF_MASTER.md` | Este archivo: contexto completo |
| `CURRENT_STATE.md` | Estado vivo, gobernanza, rutas |
| `docs/ROADMAP_PROYECTO.md` | PASO 0-7, metricas, bloqueos, cierre |
| `docs/DECISIONES_TECNICAS.md` | D-01 a D-12 |
| `CURSOR_HANDOFF.md` | Handoff para Cursor (apoyo secundario) |
| `data/piloto_ocr/CHECKLIST_POBLADO.md` | Como poblar un nuevo piloto |
| `scripts/piloto_field_extract_paso4.py` | Extractor determinista |
| `scripts/piloto_paso4_eval.py` | Evaluacion vs gold |
