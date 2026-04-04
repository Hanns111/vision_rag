# Síntesis de claves — diseño tipo “agente de código en terminal” (desde tu análisis)

**Origen:** Fuentes en `SANTO_GRIAL_ANALYSIS/` — en particular `SYSTEM_BRAIN_CONFIRMED.md`, `SYSTEM_BLUEPRINT/AGENT_BLUEPRINT.md`, `SYSTEM_BLUEPRINT/LANGGRAPH_MAPPING.md`.  
**Uso:** Guía para **reinterpretar** y construir **tu propio** sistema (p. ej. evidencia MINEDU, LangGraph, sandbox Python). **No** es el manual interno del producto comercial ni una receta para clonarlo.

---

## 1. Cadena de arranque confirmada (CLI interactivo)

1. **`src/entrypoints/cli.tsx`** — `main()` primero; `process.argv`, *fast paths* (versión, MCP, bridge, etc.).
2. Si no hay *fast path*: import dinámico **`../main.js`** → **`cliMain()`** (`export async function main()` en **`src/main.tsx`**).
3. **`main.tsx`** — política global, init, y en modo interactivo **`launchRepl`** (`replLauncher.tsx`).
4. **`launchRepl`** monta **`<App><REPL /></App>`** (Ink / React terminal UI).
5. Usuario escribe en **`src/screens/REPL.tsx`**; submit → **`handlePromptSubmit`** (`src/utils/handlePromptSubmit.ts`).
6. Callback **`onQuery`** → **`for await (const event of query({...}))`** donde **`query`** sale de **`src/query.ts`**.

**Modo bridge / remoto:** rama distinta → **`src/bridge/bridgeMain.ts`** (no es el camino REPL estándar).

---

## 2. Dónde vive el “cerebro” del turno (modelo + herramientas)

| Pregunta | Respuesta (análisis) |
|----------|----------------------|
| ¿Un solo archivo “cerebro”? | **No**: arquitectura **distribuida**. |
| ¿Lazo LLM + tools multi-paso? | **`src/query.ts`**: generador **`query`** → **`queryLoop`**, con mensajes, `toolUseContext`, `canUseTool`, `turnCount`, compactación, etc. |
| ¿Quién une UI y núcleo? | **`REPL.tsx`** + **`handlePromptSubmit.ts`**. |
| ¿Quién arranca el binario? | **`cli.tsx`**, no `main.tsx` solo. |

**Fórmula útil para copiar el diseño:**

`input (REPL) → handlePromptSubmit → query (async generator) → eventos stream → UI`

---

## 3. Flujo abstracto (blueprint, sin nombres de archivo)

```
Usuario (terminal)
  → CLI bootstrap
  → Núcleo app (flags, política, init)
  → TUI / REPL
  → Submit orchestration (comandos, colas, permisos)
  → Motor de consulta (un “turno”; puede ser multi-iteración)
  → Bucle interno: modelo ↔ herramientas ↔ compactación
  → Herramientas (archivo, shell, MCP, agente hijo, …)
  → Streaming de eventos a la UI
```

**Cadena compacta del blueprint:**  
`input → REPL → handlePromptSubmit → query → queryLoop → tools → output`

---

## 4. Herramientas y política

- Las **tools** se resuelven por nombre dentro del lazo (p. ej. patrón tipo **`findToolByName`** en el análisis de `query.ts`).
- **`canUseTool`** y contexto de permisos son el **candado** entre “el modelo pidió X” y “ejecutamos X”.
- La **validación** en un sistema propio puede modelarse como **pre-tool** (y opcionalmente post-tool).

---

## 5. Mapeo a un grafo tipo LangGraph (recomendación del análisis)

**Nodos:** `input_node` → `reasoning_node` → (si hay tool calls) `validation_node` → `tool_node` → vuelta a `reasoning_node` → `output_node`.

**Condición de parada del turno:** el razonador devuelve **sin** tool calls pendientes (o límite de iteraciones / error).

**Equivalencias informales:**

| Pieza de referencia | Nodo |
|---------------------|------|
| REPL / captura de texto | `input_node` o alimentación de estado |
| `query` / `queryLoop` | Subgrafo reasoning ↔ tool |
| `canUseTool` | Guard en `validation_node` o aristas |

---

## 6. Módulos “pesados” citados en grafos de dependencia (para lectura dirigida)

Sin pretender lista cerrada: el análisis menciona rutas como:

- **`src/services/api/claude.ts`** — capa API / proveedor.
- **`src/utils/claudemd.ts`** — convenciones de contexto tipo CLAUDE.md.
- **MCP:** `src/services/mcp/*`, handlers en `src/cli/handlers/mcp.tsx`, etc.
- **Eventos internos:** tipos bajo `src/types/generated/events_mono/claude_code/...`
- **SDK:** referencias a `@anthropic-ai/claude-agent-sdk` en índices de dependencia.

Exploración sistemática: **`PROJECT_INDEX.json`**, **`DEPENDENCY_GRAPH.md`**, **`CODIGO_FUENTE_RECONSTRUIDO/_MANIFEST.json`**.

---

## 7. Variables de entorno observadas (solo como pistas de arquitectura)

El índice del proyecto registra flags del estilo `CLAUDE_CODE_USE_CCR_V2`, `CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2`, `CLAUDE_BRIDGE_USE_CCR_V2`, etc. — útiles para entender **modos de transporte** (SSE vs híbrido) en una reimplementación **no** significa dependerte de los mismos nombres.

---

## 8. Cómo “rehacer algo parecido” sin los 60 GB en la cabeza

1. **Mantén** `SANTO_GRIAL_ANALYSIS/` como archivo histórico; no lo mezcles con `agent_sandbox` en runtime.
2. **Implementa** tu grafo (LangGraph o nodos Python) siguiendo **`LANGGRAPH_MAPPING.md`**.
3. **Valida** tu diseño contra **`SYSTEM_BRAIN_CONFIRMED.md`** (¿quién hace el async generator del turno?).
4. **Audita** con **`AGENT_SANDBOX_SOURCE_FOR_AUDIT/`** si el foco es tu stack Python + evidencia.

---

## 9. Lo que este documento **no** es

- No sustituye leer **`output/src/`** cuando necesitas una rama concreta.
- No incluye todos los miles de archivos nombrados uno a uno — eso está en **`PROJECT_TREE.md`** / **`PROJECT_INDEX.json`**.
- No autoriza ignorar licencias ni términos del software original analizado.
