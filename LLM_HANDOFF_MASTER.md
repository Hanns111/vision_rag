# LLM_HANDOFF_MASTER — Contexto maestro para cualquier LLM

> Archivo de transferencia de contexto. Cualquier LLM que lea este documento debe tener una imagen completa del proyecto, su estado, su dirección estratégica y las restricciones activas.

**Proyecto:** vision_rag  
**Repo:** Hanns111/vision_rag  
**Ruta local:** `C:\Users\Hans\Proyectos\vision_rag`  
**Rama:** `main`  
**Última actualización:** 2026-04-14

---

## 1. Qué es este proyecto

Sistema de procesamiento documental para expedientes de pago del sector público peruano (MINEDU). Tiene dos piezas separadas:

1. **RAG normativo** (`agent_sandbox/`) — operativo. Responde preguntas sobre directivas con evidencia trazable.
2. **Pipeline OCR/extracción** (PASO 0–7) — en construcción. Extrae campos estructurados de facturas, recibos y documentos escaneados.

**No** es un sistema monolítico. Las dos piezas son independientes hasta PASO 7 (integración futura con contrato de datos).

---

## 2. Estrategia actual del sistema

### El enfoque es determinista, no basado en LLM

El pipeline de extracción documental funciona **sin LLM**. Esto es una decisión de diseño deliberada, no una limitación temporal.

**Por qué se prioriza determinismo:**

- **Velocidad:** Las reglas procesan una página en milisegundos. Un LLM tarda segundos por campo.
- **Auditabilidad:** Cada campo extraído tiene una traza (`tipo_doc_inferido`, `regla`, `lineas_usadas`). Un auditor puede verificar exactamente por qué el sistema produjo un valor. Con LLM, la explicación es una caja negra.
- **Reproducibilidad:** Misma entrada = misma salida, siempre. Los LLM tienen variabilidad inherente (temperatura, versión del modelo, contexto).
- **Costo:** El pipeline corre en cualquier máquina con Tesseract. No requiere GPU, API cloud ni tokens.
- **Sin alucinaciones:** El extractor devuelve `null` si no encuentra un campo. Nunca inventa un RUC ni un monto.

**Evidencia que lo respalda (PASO 4.1, 2026-04-14):**

| Métrica | Valor |
|---------|-------|
| Mejoras netas vs extractor mínimo | **+33 aciertos** sobre 150 campos evaluados |
| Regresiones | **0** |
| monto_subtotal | **9/9** (100%) |
| serie_numero | **13/13** (100%) |
| tipo_documento | **15/15** (100%) |
| monto_total | **12/12** (100%) |
| razon_social_emisor | **8/10** (80%) — partiendo de 0% |
| Dependencia de LLM | **Ninguna** |

**Cuándo se evaluaría usar LLM:**

- Solo como **fallback** (PASO 5 del roadmap) para campos donde el extractor marca baja confianza.
- Solo **después** de validar que el pipeline determinista generaliza a expedientes nuevos.
- Solo con **techo de llamadas** (presupuesto acotado) y **log obligatorio** por cada invocación.
- Solo si los fallos residuales lo justifican cuantitativamente (hoy son 7 de 150 campos = 4.7%).

**Riesgos de introducir LLM antes de tiempo:**

- Enmascara debilidades del OCR y del parsing que deberían resolverse con reglas.
- Introduce latencia y costo sin evidencia de que el retorno lo justifique.
- Dificulta auditoría: si un LLM "corrige" un campo, no hay traza de por qué eligió ese valor.
- Crea dependencia en disponibilidad de API o GPU que el pipeline actual no tiene.
- El 43% de los fallos restantes (3/7) son OCR_NO_PRESENTE — el LLM sobre texto no los resuelve.

---

## 3. Estado actual (2026-04-14)

### PASO 0–4.1: completados y estables

| PASO | Estado | Commit | Resultado clave |
|------|--------|--------|-----------------|
| 0 | Cerrado | `54517f7` | 15/15 páginas etiquetadas, manifest coherente |
| 1 | Cerrado | `3f2a5cc` | Baseline Tesseract, CSV en metrics/ |
| 2 | Cerrado | `fc31b7f` | Bake-off 3 motores; WSL preferente (D-12) |
| 3 | Cerrado | `9ad4e8f` | Mini A/B sin mejora; no iterar preproceso |
| 4 | Cerrado | `d67e01b` | Extractor por reglas: +21 vs minimal, 0 regresiones |
| 4.1 | Cerrado | `734bb5c` | Corrección: +33 vs minimal, 0 regresiones |

### PASO 5–7: no iniciados

| PASO | Estado | Nota |
|------|--------|------|
| 5 | No abierto | Fallback LLM — no es prioridad inmediata |
| 6 | Prototipo existente | RAG normativo en `agent_sandbox/`, independiente del pipeline OCR |
| 7 | Bloqueado | Integración OCR + agente; requiere contrato de datos (D-07) |

### Fallos residuales tras PASO 4.1

| Tipo | Cantidad | Solucionable con LLM sobre texto |
|------|----------|----------------------------------|
| OCR_NO_PRESENTE | 3 | No (el campo no existe en el OCR) |
| OCR_AMBIGUO | 1 | Parcialmente (riesgo alto) |
| Layout fragmentado | 1 | Parcialmente |
| Sin señal en OCR (moneda) | 1 | No |
| Orden de tokens (nombre) | 1 | Sí, pero frágil |

---

## 4. Siguiente paso lógico

**NO es PASO 5 (LLM).** Es validación en más expedientes reales.

Razones:
- El pipeline se construyó y evaluó sobre **un solo expediente** (DEBEDSAR2026-INT-0103251, 15 páginas).
- Antes de añadir complejidad (LLM, nuevos motores, integración), hay que validar que las reglas **generalizan** a otros formatos de factura, otros proveedores, otros tipos de escaneo.
- Si las reglas generalizan: el pipeline está listo para producción sin LLM.
- Si no generalizan: los datos de fallo dirán exactamente qué ajustar (nuevas reglas, o ahí sí fallback LLM).

**Acción concreta pendiente (decisión de Hans):**
1. Seleccionar un segundo expediente de viáticos (diferente proveedor, diferente UE).
2. Etiquetar 10–15 páginas nuevas con el mismo esquema `piloto_ocr.v1`.
3. Correr el extractor PASO 4.1 sin modificar y medir.
4. Analizar fallos: ¿son reglas nuevas o limitaciones estructurales?

---

## 5. Gobernanza operativa

| Rol | Quién | Alcance |
|-----|-------|---------|
| **Decisor final** | Hans | Aprueba fases, cambios de rumbo, push a remoto |
| **Ejecutor principal** | Claude Code | Modifica archivos, commit, push — bajo decisión de Hans |
| **Apoyo secundario** | Cursor | Ejecución/documentación cuando Hans lo convoque |
| **Auditor / continuidad estratégica** | ChatGPT | Control de fase, consistencia entre herramientas |

---

## 6. Restricciones activas

- **No mezclar con subvención** (`06_subvenciones` excluida del piloto).
- **No integrar OCR al agente** hasta PASO 7 (D-07).
- **No tocar** `orchestrator.py` ni `agent_sandbox/`.
- **No reabrir roadmap** ni arquitectura.
- **LLM = último recurso**, no primera opción (R1, R2 del roadmap).

---

## 7. Decisiones técnicas vigentes (D-01 a D-12)

| ID | Decisión | Estado |
|----|----------|--------|
| D-01 | Rechazar VLM/LLM como OCR principal masivo | Cerrada |
| D-02 | Pipeline híbrido: preproceso → OCR → reglas → fallback LLM acotado | Cerrada |
| D-03 | RAG = capa posterior, no sustituto de extracción | Cerrada |
| D-04 | Docling/parsers cloud: solo tras bake-off | Cerrada |
| D-05 | PaddleOCR: candidato, sin decisión sin métricas | Abierta |
| D-06 | Baseline: `scripts/document_ocr_runner.py` | Hecho |
| D-07 | Integración OCR ↔ agente: bloqueado hasta PASO 7 | Pendiente |
| D-08 | PASO 0 documentado: N=15, 11 campos, `piloto_ocr.v1` | Cerrada |
| D-09 | 15 etiquetas + manifest completo | Cerrada |
| D-10 | Validación de identidad de expediente obligatoria | Cerrada |
| D-11 | OCR por regiones (ROI): línea futura, sin PASO asignado | Documentada |
| D-12 | Entorno preferente: Linux/WSL para OCR avanzado | Cerrada |

---

## 8. Estructura del repo

```
vision_rag/
  agent_sandbox/          # RAG normativo + agente (PASO 6, independiente)
  scripts/                # OCR baseline, extractor PASO 4, eval
  data/piloto_ocr/        # Piloto: raw/, labels/, metrics/, manifest
  docs/                   # Roadmap, decisiones, estado RAG, taxonomía
  control_previo/         # Normativa y expedientes por categoría MINEDU
  tests/
```

---

## 9. Archivos clave (leer primero)

| Archivo | Propósito |
|---------|-----------|
| `CURRENT_STATE.md` | Estado vivo del proyecto + gobernanza |
| `docs/ROADMAP_PROYECTO.md` | Roadmap PASO 0–7, métricas §4.3, cierre §9 |
| `docs/DECISIONES_TECNICAS.md` | Tabla D-01 a D-12 |
| `data/piloto_ocr/MANIFEST_PILOTO.csv` | Inventario del piloto (3 PDFs, 15 páginas) |
| `data/piloto_ocr/CHECKLIST_POBLADO.md` | Cómo poblar un nuevo piloto |
| `scripts/piloto_field_extract_paso4.py` | Extractor determinista con trazas |
| `scripts/piloto_paso4_eval.py` | Evaluación PASO 4 vs gold |

---

## 10. Para el LLM que lee esto

1. **No propongas usar LLM para extracción** salvo que Hans lo pida explícitamente.
2. **No rediseñes la arquitectura.** El pipeline funciona. Mejóralo incrementalmente.
3. **Mide antes de cambiar.** Cada ajuste debe evaluarse contra las 15 páginas del piloto con `piloto_paso4_eval.py`.
4. **Respeta el roadmap.** Los PASO son secuenciales y con criterios de cierre.
5. **Prioridad actual:** validar generalización en expedientes nuevos, no añadir capas.
