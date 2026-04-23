# SESSION_HANDOFF_NEXT_CHAT — `vision_rag`

> **Objetivo**: retomar rápido desde otro chat sin perder contexto.
> **Generado**: 2026-04-22.
> **Lectura previa obligatoria**: `docs/LLM_MASTER_CONTEXT.md` (secciones 1, 10 y **16** sobre el sandbox auditor).

---

## A. Estado actual

### Fase actual

**ABIERTA. Pendiente validación humana por Hans.**

### Qué ya funciona

- Pipeline `vision_rag` en repo (ingesta + OCR + parsing + consolidación + Excel): estable, ejecutable con `python scripts/ingest_expedientes.py run-all --src <carpeta> --expediente-id <id>`.
- 4 expedientes procesados (DEBE-0316916, DEBEDSAR-0103251, DIED-0250235, DIED-0344746). 86 comprobantes extraídos. Excel de validación humana generado en `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (NO commiteado por D-23).
- **Fuera del repo**, en sandbox: motor de auditoría determinista `control_previo_viaticos` **v2.1.0** con 161 tests passing y Excel de auditoría generado para DEBE-0316916.

### Qué está pendiente

1. **[BLOCKER]** Validación humana del Excel del pipeline por Hans (contrastar 70/86 comprobantes marcados `flag_revision_manual=SI` contra PDFs).
2. **[NUEVO]** Validación humana del Excel del auditor v2.1.0 generado en sandbox + decisión sobre integrarlo al repo.
3. **[PROPUESTO, sin autorización]** Rediseño del layout del Excel del auditor a 4 hojas tipo papeles de trabajo (ANALISIS_VIATICOS, CHECKLIST_DOCUMENTOS, OBSERVACIONES_Y_HALLAZGOS, REGISTRO_DE_COMPRAS) según modelo HCP — diseño entregado, espera frase `DISEÑO EXCEL OK — AUTORIZADO`.

---

## B. Qué se hizo en sandbox (fuera del repo)

Ruta del sandbox:

```
C:\Users\Hans\Documents\Claude\Projects\INGENIERIA INVERSA_módulo_VIÁTICOS_vision_rag\sandbox_test_cowork_v2\
```

### Logros

- Paquete externo Cowork `vision_rag_control_previo_v2.zip` extraído y extendido a **v2.1.0-determinista**.
- 14 módulos nuevos en `rules/` (subcategorias, clasificador_mef, topes_6418, tope_diario, tiempo_efectivo, hospedaje_multidia, conflictos, anexos_vigentes, informe_vs_plan, resumen_mef, dj_policy, vinculo_actividad, confianza, dj_anexo3_conceptos).
- `extractor.py`, `validator.py`, `io/excel_writer.py`, `__init__.py` actualizados a v2.1.
- Fix del bug de encoding Windows en `io/json_loader.py` (ahora con `encoding="utf-8"`).
- **161 tests passing** en `tests/` (52 heredados v2.0 + 109 nuevos v2.1, incluye invariantes I1 Σ hospedaje, I2 sin-negativos, I3 reproducibilidad).
- Excel y `audit.json` generados para DEBE2026-INT-0316916 en `sandbox_test_cowork_v2/output/`.

### Resultado de la corrida contra DEBE-0316916

- 15 CPs clasificados (6 ALIMENTACION, 6 HOSPEDAJE, 2 PASAJE_TERRESTRE, 1 NO_DETERMINABLE).
- **12 observaciones**, 7 hallazgos, 18 conformes.
- Desfase SIGA detectado correctamente: el PDF etiqueta la DJ como "Anexo 4" cuando vigente es Anexo 9.
- Falsos positivos conocidos por OCR degradado del cache (ver `RESUMEN_IMPLEMENTACION_v2_1.md` en el sandbox).

### Repo intacto

`git status` antes del handoff mostraba solo modificaciones de documentación (`CURRENT_STATE.md`, `NEXT_STEP.md`, `docs/DECISIONES_TECNICAS.md`, `.gitignore`) heredadas de turnos previos — no de esta sesión de implementación. **Ningún archivo de `scripts/`, `agent_sandbox/` o cualquier carpeta de código fue tocado.**

---

## C. Qué debe revisar el humano

### Revisión 1 — Excel del pipeline (ya existía)

```
data/piloto_ocr/metrics/validacion_expedientes.xlsx
```

Procedimiento detallado en `NEXT_STEP.md`. Sin cambios en esta sesión.

### Revisión 2 — Excel del sandbox auditor (NUEVO)

```
C:\Users\Hans\Documents\Claude\Projects\INGENIERIA INVERSA_módulo_VIÁTICOS_vision_rag\sandbox_test_cowork_v2\output\AUDIT_DEBE2026-INT-0316916_v2_1.xlsx
```

Preguntas concretas que Hans debe responder al abrirlo:

1. ¿El layout sirve como papeles de trabajo o requiere el rediseño a 4 hojas tipo modelo HCP?
2. ¿Las 12 observaciones listadas son sustantivamente correctas? ¿Alguna es falso positivo que deba corregirse?
3. ¿La clasificación MEF por comprobante cuadra con el criterio operativo (pasajes vs viáticos vs combustible vs otros gastos de viaje)?
4. ¿Los topes 6.4.18, diario S/320 y DJ 30% están bien aplicados?
5. ¿La detección de desfase SIGA (Anexo 4 → Anexo 9) es correcta?

---

## D. Qué sigue exactamente

### Camino A — Hans valida el Excel del auditor

Dos sub-caminos posibles:

**A.1** — El layout actual del Excel del auditor es suficiente:
- Hans dice `AUTORIZADO INTEGRACIÓN AL REPO`.
- Se procede con la secuencia de integración (ver `docs/LLM_MASTER_CONTEXT.md §16.5`): copiar `src/control_previo_viaticos/` a `scripts/ingesta/`, copiar tests, añadir subcomando `auditar`, registrar D-24, correr pytest.

**A.2** — El layout necesita el rediseño a 4 hojas HCP:
- Hans dice `DISEÑO EXCEL OK — AUTORIZADO`.
- Se reescribe **solo** `sandbox_test_cowork_v2/vision_rag_control_previo_v2/src/control_previo_viaticos/io/excel_writer.py` (sin tocar lógica del motor, sin tocar tests, sin tocar el repo).
- Se regenera el Excel del sandbox. Hans lo revisa. Si aprueba, se va a A.1.

### Camino B — Hans encuentra errores en el auditor

- Si los errores son de layout: se itera `excel_writer.py` en el sandbox.
- Si los errores son de reglas (clasificación mal, topes mal aplicados, base legal equivocada): se itera el módulo correspondiente en `rules/` en el sandbox.
- **Siempre en sandbox hasta autorización explícita.**

### Camino C — Hans dice "cerremos primero la validación del pipeline"

- Se posterga todo lo del auditor.
- Se enfoca en el Excel del pipeline (`data/piloto_ocr/metrics/validacion_expedientes.xlsx`) según `NEXT_STEP.md`.
- El sandbox queda en pausa.

---

## E. Frases útiles para retomar

### Frases de autorización que el humano puede usar

- `AUTORIZADO ESCRITURA SANDBOX` → permite modificar `sandbox_test_cowork_v2/` sin tocar el repo.
- `DISEÑO EXCEL OK — AUTORIZADO` → reescribir `excel_writer.py` del sandbox.
- `AUTORIZADO INTEGRACIÓN AL REPO` → procede la integración según §16.5 del master context.
- `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR` → permite commitear `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (D-23).

### Mantras operativos para el continuador

- **No asumir integración**: el paquete v2.1.0 vive en sandbox, el repo está intacto; verificar con `git status` al abrir.
- **Esperar validación humana**: sin que Hans revise el Excel del sandbox o del pipeline, no hay cierre de fase ni integración.
- **Respetar D-13 y D-23**: JSON consolidado es fuente de verdad técnica; Excel es artefacto humano, no se commitea sin autorización explícita.
- **Determinismo no negociable**: no introducir LLM, embeddings, distancia semántica ni heurística blanda en `rules/`. Sin match → `NO_DETERMINABLE`.
- **Siguiente instrucción probable**: Hans abrirá el Excel del sandbox y pedirá (a) rediseño a 4 hojas tipo HCP, o (b) integración al repo, o (c) correcciones puntuales a reglas.
- **Si el continuador duda**: leer `docs/LLM_MASTER_CONTEXT.md §16` antes de proponer nada. No tocar el repo sin autorización explícita.

### Primera acción al abrir otro chat

```
git status                     # confirmar repo intacto
git log -1 --oneline           # confirmar último commit
cat docs/SESSION_HANDOFF_NEXT_CHAT.md   # leer este archivo
cat docs/LLM_MASTER_CONTEXT.md          # leer completo (§16 obligatorio)
```

Si `git status` muestra cambios en `scripts/` o `agent_sandbox/` → investigar antes de proceder.
Si no muestra nada en código: confirma que el sandbox no tocó el repo → todo OK para continuar según lo que Hans pida.

---

## F. VALIDACIÓN OCR DJ — CUELLO DE BOTELLA CONFIRMADO (2026-04-22)

**Hallazgo crítico validado empíricamente en la sesión 2026-04-22:**
el problema del DJ del expediente `DEBE2026-INT-0316916` **no está en el
parser ni en el Excel**; está en el **OCR upstream**.

### Evidencia resumida
- PDF real: **21 ítems DJ**, total S/ 165.00.
- OCR cache: **19 líneas** con fecha en la región Anexo 4 → 2 ítems enteros perdidos.
- De esas 19 líneas: **7 importes bien formados + 12 corruptos/ilegibles** (`500`, `2500`, `ali`, `—`, `Te`, `OO`).
- El total S/ 165.00 **sí se transcribe correctamente** en el OCR — el desglose por fila es lo que falla.

### Confirmación del parser
- Parser post-fix (sandbox) captura 19/19 líneas visibles.
- Asigna `numero_item` (1..19) y `pagina_pdf` (3).
- Aplica regex estricto `\d+[\.,\s]\d{2}` → 7 parseables (Σ S/ 53.04) + 12 pendientes marcados `IMPORTE_ILEGIBLE_PENDIENTE`.
- Saneamiento auxiliar `R-AUX-DJ-SANEAMIENTO`: **0 descartes**.

### Conclusión
**OCR upstream es el bloqueo técnico actual, no parsing.**

### Qué sigue mañana (primera corrección si se autoriza)

Segunda pasada OCR focalizada en la región DJ del PDF de rendición.
Patrón análogo a `scripts/ingesta/ocr_region_totales.py` (ya existe para
totales de CPs), con DPI 600-800, binarización adaptativa, y opcionalmente
`pytesseract.image_to_data` para reconstruir importes celda a celda.

**Ubicación:** repo `vision_rag`, carpeta `scripts/ingesta/`. **Fuera del sandbox.**
**Requiere:** autorización explícita para tocar pipeline principal
(hoy, bajo el guardián, esa autorización NO está dada).

### Evidencia completa

`docs/evidencia/ocr_dj_diagnostico_2026-04-22.md` — volcado literal del
OCR, conteos, clasificación de errores, referencias cruzadas.

### Mantra para el continuador

- **NO intentar arreglar DJ tocando más el parser.** Está correcto — se validó.
- **NO interpretar "500" como "5.00"** — heurística prohibida por decisión del usuario.
- Si el continuador pregunta "¿qué pasa con el total DJ?", la respuesta es: **OCR upstream, no parser**. Referenciar esta sección y el archivo de evidencia.
