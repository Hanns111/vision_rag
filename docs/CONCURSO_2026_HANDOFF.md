# CONCURSO 2026 — Handoff y plan de demo

> Documento de estado y plan operativo para preparar la presentación al concurso.
> **Fecha de cierre de sesión:** 2026-04-30.
> **Próxima sesión:** Día 1 del plan de mañana (sección 7).

---

## 1) Estado actual al 2026-04-30

- **Mini-demo técnica PASO 4.5 ejecutada en vivo desde `main`** sobre el piloto `DEBEDSAR2026-INT-0103251`.
- **Resultado del motor determinista:** `decision_global=REVISAR`, **9 hallazgos**, distribución de reglas: `R-CAMPO-CRITICO-NULL=OK`, `R-FIRMAS=OBSERVAR`, `R-CONSISTENCIA=REVISAR` (1 `DATOS_INSUFICIENTES` + 5 `DIFERENCIA_CRITICA`), `R-IDENTIDAD-EXPEDIENTE=REVISAR`, `R-UE-RECEPTOR=REVISAR`.
- **Agregación verificada:** la decisión global aplica precedencia con cortocircuito (`decision_engine.py:80-85`) — 3 reglas en `REVISAR` → cortocircuito directo a `REVISAR`. La severidad solo ordena hallazgos, no decide.
- **Idempotencia byte por byte confirmada** dentro de la sesión: dos corridas consecutivas con `--deterministico` produjeron sha256 idéntico (`b33e2dcd…`). El sub-objeto `metadata_corrida` (run_id + timestamp + host + git_commit) varía como diseñado y queda excluido del payload reproducible.
- **Motor sin escritura a disco:** ejecutado sin `--out`, solo stdout. `decision_engine.py:235-236` confirma que el CLI **solo** escribe a disco cuando se pasa `--out` explícito.
- **Hash de input estable:** `expediente.json` del piloto = `2c6ff80e6af88043664e79f5695d773acb3b75f4b2c00bf7439794ed35c8ff43` (coincide con `CURRENT_STATE.md:433`).
- **Suite de tests:** `69/69` verde según documentación de cierre del 2026-04-28 (`CURRENT_STATE.md:416,425`, `NEXT_STEP.md:9,108`). No re-ejecutada en esta sesión para no actualizar `.pytest_cache`/`__pycache__`.
- **Repo limpio sobre `main`** salvo el Excel piloto untracked `data/piloto_ocr/metrics/validacion_DEBEDSAR2026-INT-0103251_v4_piloto.xlsx` (política D-23 vigente).
- **Cursor / CURSOR_LAB en pausa total.** La rama operativa de Cursor (`cursor-operativo-control-previo`) fue creada y borrada limpiamente sin commits propios. La carpeta CURSOR_LAB no se ha creado todavía.
- **`agent_sandbox/` intacto.** Núcleo del RAG normativo sin tocar.
- **Rama preexistente `claude/flamboyant-blackwell`** detectada al cierre, no tocada, requiere decisión separada.

### Observación que requiere reconciliación

⚠️ El payload sha256 actual del motor (`b33e2dcd…`) **difiere** del documentado el 28-abr (`b6f86ff35a…fb0ac9` en `CURRENT_STATE.md:434`). El input no cambió. Hipótesis: cambio menor en el motor o su serialización entre el 28 y el 30 de abril. **No afecta la idempotencia probada hoy** (las dos corridas de la sesión coinciden), pero conviene reconciliar antes de difundir un hash como invariante histórico.

---

## 2) Verdad importante — esto NO es producto final

Lo demostrado hoy es el **motor deterministico funcionando**. Eso es el corazón técnico, pero **no** es la presentación al jurado.

Lo que falta:

- **Revisión del Excel** consolidado (`validacion_expedientes.xlsx`) — 70 de 86 comprobantes con `flag_revision_manual=SI` siguen sin contraste manual contra PDFs originales.
- **Validación visual de casos contra los PDFs** — confirmar que las observaciones del motor coinciden con lo que un revisor humano vería al abrir el documento.
- **Frontend** — hoy no existe interfaz para el jurado. Solo CLI.
- **Hosting / nube** — todo corre en la PC local de Hans. El jurado no puede depender de eso.
- **Manual de uso para jurado** — no existe.
- **Mecanismo de carga de archivos** — no está definido cómo el jurado proporcionará el insumo (¿sube PDF? ¿elige de un set preparado? ¿usa expedientes de demo embebidos?).
- **Anonimización para difusión pública** — RUC del MINEDU (`20380795907`) y montos son visibles en los outputs actuales.
- **Modo demo pública vs interna** — falta política clara.

---

## 3) Objetivo de concurso

Presentar **una iniciativa/piloto de control previo auditable para expedientes**. No "PASO 4.5". El nombre técnico interno no es el mensaje al jurado.

### Roles claros

- **Motor determinista:** decide y/o recomienda. Es el juez técnico. Reglas atómicas, auditables, idempotentes.
- **IA local:** explica, responde preguntas del jurado, cita fuente y base legal. **Nunca juzga.** Si no encuentra evidencia, dice "no encontrado" en vez de inventar.

Esta separación es el principio rector del proyecto (D-25). El concurso debe transmitirla con claridad.

---

## 4) Alcance de la demo

Elegir **3 casos demostrables** a partir del corpus actual (4 expedientes ingestados, 86 comprobantes).

Cada caso debe tener todos estos elementos antes de presentarse:

- **a)** Archivo (o paquete) cargable por el jurado — definir formato exacto.
- **b)** Resultado determinista del motor — `decision_global` + hallazgos + reglas evaluadas.
- **c)** Evidencia visible — capacidad de abrir el PDF o ver el extracto que motivó cada hallazgo.
- **d)** Base legal asociada — numeral exacto de la directiva o normativa aplicable.
- **e)** Respuesta explicable por IA local — el jurado debe poder preguntar y recibir respuesta con cita.
- **f)** Fallback si visión / OCR falla — qué pasa cuando el OCR no captura un campo, cómo se reporta, cómo se sugiere subsanación.
- **g)** Estado "requiere revisión humana" cuando corresponda — reconocer límites del motor sin enmascararlos.

---

## 5) Flujo deseado para el jurado

```
1. Jurado abre el frontend (web local o hosting temporal).
2. Carga 3 archivos o selecciona de un paquete de demo preparado.
3. El sistema procesa en vivo o lee artefactos pre-generados.
4. Pantalla de resumen: identidad del expediente, decisión global, conteo de hallazgos.
5. Lista de hallazgos clasificados por regla.
6. Cada hallazgo enlaza a la evidencia (PDF / extracto resaltado).
7. Caja de chat con IA local: el jurado pregunta, la IA responde citando base legal.
8. Cada respuesta de la IA cita: fuente (archivo/página), base legal (numeral/directiva).
9. Si la IA no tiene evidencia, responde "no encontrado", no inventa.
10. Mini manual de uso accesible desde la primera pantalla.
```

---

## 6) Pendientes técnicos (orden sugerido)

1. **Revisar Excel** consolidado (`validacion_expedientes.xlsx`) priorizando `flag_revision_manual=SI`.
2. **Seleccionar 3 casos** representativos para la demo (uno con OK limpio, uno con REVISAR, uno con OBSERVAR — o la combinación más didáctica).
3. **Diseñar frontend en Figma** — pantallas mínimas según sección 5.
4. **Generar UI con v0 de Vercel** a partir del Figma.
5. **Integrar frontend local** con el motor determinista.
6. **Definir carga de archivos** — formato exacto, validación de input, fallback si OCR falla.
7. **Decidir hosting temporal** para no depender de la PC de Hans (Vercel, Render, Railway, etc.).
8. **Definir modo demo pública con anonimización** — sustituir RUC reales por placeholders, montos opcionales, nombres redactados.
9. **Preparar manual breve** (1-2 páginas) para el jurado.
10. **Preparar ficha Anexo 1 del concurso** según bases.

---

## 7) Plan de mañana (Día 1)

Foco operativo del 2026-05-01:

- Abrir y entender el Excel consolidado.
- Elegir 3 casos para la demo (con criterio didáctico, no solo técnico).
- Validar esos 3 casos contra los PDFs originales (golden path manual).
- Definir qué archivos exactos cargará el jurado (PDF crudo, JSON pre-procesado, paquete ZIP, etc.).
- Definir pantallas del frontend (boceto en papel o Figma).
- Decidir hosting temporal (opciones a evaluar: Vercel, Render, Railway, túnel local con Cloudflare/ngrok).
- Preparar prompt para Figma / v0 con las pantallas mínimas.

**Salida esperada del Día 1:** lista de 3 casos validados + boceto de pantallas + decisión de hosting + prompt v0 listo para ejecutar el Día 2.

---

## 8) Restricciones vigentes

- No tocar motor ni reglas sin autorización explícita.
- No regenerar el Excel principal `validacion_expedientes.xlsx`.
- No migrar los 3 expedientes restantes a `expediente.v4` sin autorización.
- No commitear el Excel piloto (D-23).
- No subir datos sensibles a nube pública (RUC, montos, nombres).
- No usar IA como juez — solo como explicador con citas.
- No abrir CURSOR_LAB todavía. Pausa total sobre Cursor.
- No tocar `agent_sandbox/`. Es núcleo del RAG normativo.
- No tocar la rama `claude/flamboyant-blackwell` sin decisión separada.

---

## Referencias

- Estado técnico completo: [`CURRENT_STATE.md`](../CURRENT_STATE.md)
- Siguiente paso operativo: [`NEXT_STEP.md`](../NEXT_STEP.md)
- Decisiones D-01…D-25: [`DECISIONES_TECNICAS.md`](DECISIONES_TECNICAS.md)
- Roadmap maestro: [`ROADMAP_PROYECTO.md`](ROADMAP_PROYECTO.md)
- Política Excel D-23: [`NEXT_STEP.md:65,150`](../NEXT_STEP.md)
- Schema `expediente.v4`: D-24
- Motor `decision_engine.v1`: D-25
