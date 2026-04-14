# AGENT_RULES — Reglas de alineación para agentes

**Alcance:** este documento gobierna el comportamiento de cualquier agente
(Claude Code, Cursor, y otros) que opere sobre el repositorio `vision_rag`.

**Referencias canónicas obligatorias:**
- `SESSION_STATE.md` (raíz) — estado actual y gobernanza vigente.
- `CURRENT_STATE.md` (raíz) — estado del sistema + gobernanza operativa.
- `docs/CURRENT_STATE_RAG.md` — estado del núcleo RAG normativo.
- `docs/ROADMAP_PROYECTO.md` — orden PASO 0–7 y reglas fijas.
- `docs/DECISIONES_TECNICAS.md` — decisiones D-01…D-12.
- `CURSOR_HANDOFF.md` (raíz) — handoff operativo para Cursor.

---

## 1. Principio general

Los agentes deben basarse en el **estado real del repositorio**, no en
suposiciones ni en memoria de sesiones previas.

- No inventar arquitectura. Si una estructura no existe en el repo, no se
  afirma que existe.
- No asumir implementaciones inexistentes. Si un módulo no está en `scripts/`
  o `agent_sandbox/`, no se habla de él como operativo.
- Antes de afirmar que algo "funciona", el agente debe verificarlo en el
  código, en los datos, o en `SESSION_STATE.md §3`.
- La memoria de un agente describe lo que era cierto **cuando se escribió**.
  Antes de actuar sobre un recuerdo, confirmarlo con el estado actual.

---

## 2. Roles de agentes (gobernanza operativa)

| Rol | Quién | Alcance |
|---|---|---|
| **Decisor final** | **Hans** | Aprueba fases, cambios de rumbo, push a remoto |
| **Ejecutor principal (implementación)** | **Claude Code** | Modifica archivos, hace commit y push bajo autorización de Hans |
| **Apoyo secundario (documentación / diseño)** | **Cursor** | Especificaciones, schemas, reglas declarativas, documentos de diseño |
| **Auditor / continuidad estratégica** | **ChatGPT** | Control de fase, validación de consistencia entre herramientas |

**Regla cardinal:** Claude Code puede ejecutar cambios en el repo (edición,
commit, push) pero **no** toma decisiones de alcance ni abre fases sin
aprobación explícita de Hans.

**Separación preservada:**
- Claude Code = **implementación** (código, tests, integración, Excel).
- Cursor = **documentación / diseño** (md/yaml/json descriptivos, sin código
  ejecutable en el pipeline).
- Hans = **decisión final**.

---

## 3. Reglas de operación

### 3.1 Antes de cualquier acción

Siempre revisar, en este orden:

1. **`SESSION_STATE.md`** — estado del último cierre de sesión (qué funciona,
   qué no, cuál es el próximo paso).
2. **`CURRENT_STATE.md`** — gobernanza operativa y estado RAG/OCR actual.
3. **`docs/`** — documentación técnica por módulo.
4. **`scripts/`** — implementación real (es la fuente de verdad sobre qué
   existe y cómo se comporta).
5. **`git log -1 --oneline`** — último commit; confirma que no hay drift
   entre memoria y repo.

### 3.2 Restricciones duras

- **No modificar código sin instrucción explícita de Hans.** Documentación
  interna de una sesión ≠ autorización para tocar lógica.
- **No crear módulos fuera del pipeline existente.** Si un nuevo módulo es
  necesario, primero se propone en diseño (Cursor) y se aprueba por Hans.
- **No renombrar, mover, ni eliminar archivos** sin justificación escrita en
  el commit y confirmación previa.
- **No usar `git push --force`, `git reset --hard`, ni bypass de hooks**
  (`--no-verify`, `--no-gpg-sign`) salvo pedido explícito.
- **No introducir dependencias nuevas** sin agregarlas a
  `scripts/requirements-ocr.txt` (o el requirements que corresponda) y
  documentarlas.

### 3.3 Restricciones de datos

- **No inventar datos.** Si un campo no se puede extraer del texto o del
  OCR, se deja `null` con `confianza = 0`. Nunca se estima.
- **No forzar resolución en conflicto.** Si dos identificadores tienen
  evidencia similar, el estado es `CONFLICTO_EXPEDIENTE`; el humano decide.
- **Trazabilidad obligatoria:** cada dato extraído debe registrar su fuente
  (archivo, página, regla, fragmento) donde el esquema lo permita.

---

## 4. Alineación con el pipeline

El pipeline de ingesta tiene un orden **canónico** que los agentes deben
respetar:

```
INGESTA
  → OCR / TEXTO (por página, text_reader v2)
  → CLASIFICACIÓN (classifier, 9 categorías + tipo_desconocido)
  → EXTRACCIÓN (PASO 4.1 — piloto_field_extract_paso4)
  → RESOLUCIÓN DE IDENTIDAD (id_resolver: SINAD, SIAF, EXP, AÑO)
  → COMPROBANTES (detector + extractor, solo si tipo=rendicion)
  → CONSOLIDACIÓN (expediente.json schema v3)
  → VALIDACIONES (firmas_anexo3, solo si tipo=rendicion)
  → EXCEL (5 hojas: documentos, expedientes, errores,
           resolucion_ids, comprobantes)
```

Reglas de alineación:

- **No saltar pasos.** No se añaden validaciones antes de que el paso
  correspondiente esté consolidado en `expediente.json`.
- **Aditivo, no destructivo.** Un paso nuevo se suma; no reescribe las
  salidas públicas de los pasos anteriores.
- **Desacoplado.** Cada paso debe poder desactivarse (`--skip-*`) y el
  pipeline debe continuar aunque una etapa opcional falle.
- **Idempotente.** Cache por sha1 de archivo; upsert por clave estable
  en el Excel.

Rutas clave del pipeline:

| Qué | Dónde |
|---|---|
| CLI principal | `scripts/ingest_expedientes.py` |
| Ingesta | `scripts/ingesta/scanner.py`, `text_reader.py`, `classifier.py`, `extractor.py`, `id_resolver.py`, `comprobante_detector.py`, `comprobante_extractor.py`, `excel_export.py` |
| Validaciones | `scripts/validaciones/firmas_anexo3.py` |
| Modelo | `scripts/modelo/expediente.py` (schema `expediente.v3`) |
| Consolidador | `scripts/consolidador.py` |
| Excel | `data/piloto_ocr/metrics/validacion_expedientes.xlsx` |
| Expediente piloto | `control_previo/procesados/DIED2026-INT-0250235/` |

---

## 5. Reglas de respuesta

### 5.1 Contenido

- **Evitar respuestas genéricas.** Nombrar archivos, funciones, líneas,
  commits cuando corresponda (`archivo:línea`, `hash 7 chars`).
- **Basarse en archivos reales del repo.** Si se cita una ruta, debe
  existir. Si se cita una regla de negocio, debe estar documentada.
- **Preguntar si falta contexto.** Si una instrucción es ambigua o hay
  ≥2 interpretaciones plausibles, preguntar antes de ejecutar. No
  asumir por omisión.
- **Diferenciar lo implementado de lo documentado.** El hecho de que algo
  esté en `docs/modulos/` no significa que esté en el pipeline.

### 5.2 Forma

- **Concisa por defecto.** Resultado + una línea de contexto + siguiente
  paso. Sin resúmenes decorativos al final de cada turno.
- **Sin narración del proceso interno.** Los usuarios leen diffs y outputs,
  no deliberaciones.
- **Marcar honestamente las limitaciones.** Si el OCR cubre 12% de montos,
  se dice 12%, no "cobertura parcial".

### 5.3 Antes de proponer implementación

- Describir arquitectura.
- Listar archivos nuevos / modificados.
- Indicar riesgos conocidos.
- Esperar aprobación explícita de Hans (coherente con §2).

---

## 6. Versionado

Este archivo **gobierna el comportamiento de los agentes** que operan sobre
el repositorio.

- Cualquier cambio a las reglas de este documento debe **versionarse con
  commit explícito** describiendo el motivo.
- Un cambio en `AGENT_RULES.md` puede invalidar memorias de agentes previas
  → los agentes deben releerlo al comenzar cada sesión.
- Conflictos entre `AGENT_RULES.md` y memoria de un agente: **gana este
  archivo**.
- Conflictos entre `AGENT_RULES.md` y `SESSION_STATE.md` del cierre más
  reciente: **gana el documento más específico al contexto**; si persiste
  ambigüedad, preguntar a Hans.

---

## 7. Validación rápida al inicio de sesión

Un agente que arranca una nueva sesión debería verificar, en menos de
30 segundos:

```bash
git status
git log -1 --oneline
cat SESSION_STATE.md      # leer al menos §3 (qué funciona) y §4 (próximo paso)
cat docs/AGENT_RULES.md   # este archivo
```

Si estas cuatro lecturas entran en conflicto entre sí, **pausar** y
preguntar antes de actuar.

---

*Creado: 2026-04-14. Gobierna el comportamiento de agentes sobre
`vision_rag` desde esta fecha.*
