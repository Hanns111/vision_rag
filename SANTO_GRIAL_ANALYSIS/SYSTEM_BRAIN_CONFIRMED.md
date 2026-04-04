# SYSTEM_BRAIN_CONFIRMED.md

Análisis basado solo en el código bajo `SANTO_GRIAL_ANALYSIS/output/src/` (reconstruido del source map). No se infiere comportamiento en runtime más allá de lo que encadenan las funciones.

---

## 1. Entry point real

### Proceso Node / binario (primer módulo ejecutado en la app CLI)

El **primer `main()` que corre** en la ruta interactiva normal es el de **`src/entrypoints/cli.tsx`**: al final del archivo se invoca `void main()`.

Ese `main`:

- Lee `process.argv.slice(2)`.
- Atiende **fast paths** (versión, MCP, bridge, daemon, plantillas, etc.).
- Si no hay fast path, hace `startCapturingEarlyInput()`, importa dinámicamente **`../main.js`** y llama a la función exportada como `main` renombrada a `cliMain`:

```287:298:output/src/entrypoints/cli.tsx
  // No special flags detected, load and run the full CLI
  const {
    startCapturingEarlyInput
  } = await import('../utils/earlyInput.js');
  startCapturingEarlyInput();
  profileCheckpoint('cli_before_main_import');
  const {
    main: cliMain
  } = await import('../main.js');
  profileCheckpoint('cli_after_main_import');
  await cliMain();
  profileCheckpoint('cli_after_main_complete');
```

```301:302:output/src/entrypoints/cli.tsx
// eslint-disable-next-line custom-rules/no-top-level-side-effects
void main();
```

### `src/main.tsx`

Define **`export async function main()`**, que concentra inicialización (entorno, señales, flags, Commander, políticas, etc.) y, en los modos interactivos pertinentes, **lanza el REPL Ink** mediante `launchRepl` (importado desde `./replLauncher.js`).

Conclusión: **entrada lógica del producto CLI = `cli.tsx` → `main.tsx#main()`.**  
`main.tsx` no es el primer archivo evaluado; es el **núcleo de arranque del CLI completo** después del bootstrap.

### `src/bridge/bridgeMain.ts`

**No es el entrypoint del uso interactivo por defecto.** Solo entra en juego cuando el usuario ejecuta el modo *remote control* / bridge (p. ej. argumentos `remote-control`, `rc`, `remote`, `sync`, `bridge`), rama que en `cli.tsx` importa `bridgeMain` y la ejecuta:

```112:161:output/src/entrypoints/cli.tsx
  if (feature('BRIDGE_MODE') && (args[0] === 'remote-control' || args[0] === 'rc' || args[0] === 'remote' || args[0] === 'sync' || args[0] === 'bridge')) {
    // ...
    const {
      bridgeMain
    } = await import('../bridge/bridgeMain.js');
    // ...
    await bridgeMain(args.slice(1));
    return;
  }
```

`bridgeMain` arranca otro flujo (parseo de args, `enableConfigs`, `initSinks`, bucles de sesión/spawn, etc.):

```1980:1985:output/src/bridge/bridgeMain.ts
export async function bridgeMain(args: string[]): Promise<void> {
  const parsed = parseArgs(args)

  if (parsed.help) {
    await printHelp()
```

### `src/screens/REPL.tsx`

**No inicia el proceso:** es el **componente de UI** que vive **dentro de Ink** tras `launchRepl`. Ahí es donde el usuario escribe en el terminal y se despacha el turno hacia la lógica de “query”.

`launchRepl` monta explícitamente `<App><REPL … /></App>`:

```12:21:output/src/replLauncher.tsx
export async function launchRepl(root: Root, appProps: AppWrapperProps, replProps: REPLProps, renderAndRun: (root: Root, element: React.ReactNode) => Promise<void>): Promise<void> {
  const {
    App
  } = await import('./components/App.js');
  const {
    REPL
  } = await import('./screens/REPL.js');
  await renderAndRun(root, <App {...appProps}>
      <REPL {...replProps} />
    </App>);
}
```

---

## 2. Flujo de ejecución paso a paso (modo interactivo TUI)

1. **`cli.tsx` `main()`** — bootstrap y fast paths.
2. **`await import('../main.js'); await cliMain()`** — entra en **`main.tsx` `export async function main()`** (configuración global y rutas CLI).
3. **`launchRepl(...)`** (`replLauncher.tsx`) — **`renderAndRun`** con **`<REPL />`**.
4. En **`REPL.tsx`** — el usuario confirma entrada; en el camino analizado, el submit llama **`handlePromptSubmit`** (desde `../utils/handlePromptSubmit.js`) pasando **`onQuery`** entre otros parámetros.
5. **`onQuery`** (callback en REPL) arma contexto (p. ej. system prompt efectivo) y entra en el lazo **`for await (const event of query({ ... }))`**, que consume el generador **`query`** de `../query.js`.

```2788:2803:output/src/screens/REPL.tsx
    queryCheckpoint('query_query_start');
    resetTurnHookDuration();
    resetTurnToolDuration();
    resetTurnClassifierDuration();
    for await (const event of query({
      messages: messagesIncludingNewMessages,
      systemPrompt,
      userContext,
      systemContext,
      canUseTool,
      toolUseContext,
      querySource: getQuerySourceForREPL()
    })) {
      onQueryEvent(event);
    }
```

6. **`handlePromptSubmit`** — punto de orchestración entre modo, colas, comandos slash y la llamada a **`onQuery`** (el archivo documenta ejecución núcleo vs UI):

```78:84:output/src/utils/handlePromptSubmit.ts
/**
 * Parameters for core execution logic (no UI concerns).
 */
type ExecuteUserInputParams = BaseExecutionParams & {
  resetHistory: () => void
  onInputChange: (value: string) => void
}
```

Ejemplo de cadena en REPL → `handlePromptSubmit` → `onQuery`:

```3488:3519:output/src/screens/REPL.tsx
    // Ensure SessionStart hook context is available before the first API call.
    await awaitPendingHooks();
    await handlePromptSubmit({
      input,
      helpers,
      queryGuard,
      isExternalLoading,
      mode: inputMode,
      commands,
      onInputChange: setInputValue,
      setPastedContents,
      setToolJSX,
      getToolUseContext,
      messages: messagesRef.current,
      mainLoopModel,
      pastedContents,
      ideSelection,
      setUserInputOnProcessing,
      setAbortController,
      abortController,
      onQuery,
      setAppState,
      querySource: getQuerySourceForREPL(),
      onBeforeQuery,
      canUseTool,
      addNotification,
      setMessages,
      // Read via ref so streamMode can be dropped from onSubmit deps —
      // handlePromptSubmit only uses it for debug log + telemetry event.
      streamMode: streamModeRef.current,
      hasInterruptibleToolInProgress: hasInterruptibleToolInProgressRef.current
    });
```

7. **`query.ts`** — **`export async function* query`** delega en **`queryLoop`**, que es el estado explícito del bucle por turno (mensajes, `toolUseContext`, compactación, etc.):

```219:239:output/src/query.ts
export async function* query(
  params: QueryParams,
): AsyncGenerator<
  | StreamEvent
  | RequestStartEvent
  | Message
  | TombstoneMessage
  | ToolUseSummaryMessage,
  Terminal
> {
  const consumedCommandUuids: string[] = []
  const terminal = yield* queryLoop(params, consumedCommandUuids)
  // Only reached if queryLoop returned normally. Skipped on throw (error
  // propagates through yield*) and on .return() (Return completion closes
  // both generators). This gives the same asymmetric started-without-completed
  // signal as print.ts's drainCommandQueue when the turn fails.
  for (const uuid of consumedCommandUuids) {
    notifyCommandLifecycle(uuid, 'completed')
  }
  return terminal
}
```

```241:279:output/src/query.ts
async function* queryLoop(
  params: QueryParams,
  consumedCommandUuids: string[],
): AsyncGenerator<
  | StreamEvent
  | RequestStartEvent
  | Message
  | TombstoneMessage
  | ToolUseSummaryMessage,
  Terminal
> {
  // Immutable params — never reassigned during the query loop.
  const {
    systemPrompt,
    userContext,
    systemContext,
    canUseTool,
    fallbackModel,
    querySource,
    maxTurns,
    skipCacheWrite,
  } = params
  const deps = params.deps ?? productionDeps()

  // Mutable cross-iteration state. ...
  let state: State = {
    messages: params.messages,
    toolUseContext: params.toolUseContext,
    ...
    turnCount: 1,
```

Este módulo importa utilidades de mensajes, API, **`findToolByName`** desde `./Tool.js`, compactación, etc., lo que encaja con **selección y ejecución de tools dentro del lazo**, sin necesidad de adivinar órdenes concretos de cada rama.

---

## 3. Agent loop confirmado

Patrón observable en código (modo REPL interactivo):

| Etapa | Dónde se ancla en código |
|--------|---------------------------|
| **Input usuario** | `REPL.tsx` — `PromptInput` / submit → `handlePromptSubmit` |
| **Procesamiento / cola / comandos** | `handlePromptSubmit.ts` + `processUserInput` (importado allí) |
| **Llamada al modelo + tools** | `query.ts` — `query` → `queryLoop`; parámetros incluyen `canUseTool`, `toolUseContext` |
| **Salida / eventos de streaming** | `REPL.tsx` — `onQueryEvent(event)` dentro del `for await` sobre `query()` |

**Validación y políticas** aparecen en varias capas (p. ej. `canUseTool`, permisos, hooks); el detalle por rama está dentro de `queryLoop` y módulos importados — no se resume aquí sin citar cada bifurcación.

---

## 4. Archivo(s) que actúan como cerebro — **SYSTEM_BRAIN_CONFIRMADO**

No hay **un único archivo** que cumpla simultáneamente “solo entrypoint”, “solo UI”, “solo lazo del modelo” y “solo tools”. La arquitectura está **distribuida**:

| Rol | Archivo(s) | Evidencia |
|-----|------------|-----------|
| **Entrada de proceso CLI** | `src/entrypoints/cli.tsx` | `void main()`; import dinámico de `main.js` y `await cliMain()` |
| **Arranque y ensamblaje del CLI** | `src/main.tsx` | `export async function main()`; orchestración global hasta `launchRepl` |
| **UI + recepción de input + disparo de turno** | `src/screens/REPL.tsx` | `handlePromptSubmit`; `for await (... query(...))` |
| **Puente submit → ejecución núcleo** | `src/utils/handlePromptSubmit.ts` | Tipos “core execution”; `onQuery` en parámetros |
| **Lazo operativo modelo + tools (un turno / multi-iteración interna)** | **`src/query.ts`** (`query` / `queryLoop`) | Generador async; estado `toolUseContext`, `canUseTool`, `turnCount` |
| **Modo remoto / bridge (otro producto de ejecución)** | `src/bridge/bridgeMain.ts` | Solo si argv entra en rama bridge en `cli.tsx` |

**Veredicto:** el **“cerebro” del agente en el sentido de lazo LLM + herramientas** está **confirmado** en **`src/query.ts`**. La **orquestación producto → pantalla REPL → submit** está en **`REPL.tsx` + `handlePromptSubmit.ts`**. El **punto de entrada real del binario/CLI** es **`cli.tsx`**, no `main.tsx` solo ni `REPL.tsx` solo.

La hipótesis anterior que elevaba `main.tsx` como único SYSTEM_BRAIN mezclaba **alto fan-in / peso del índice** con el **papel exacto en la cadena de llamadas**: `main.tsx` es indispensable para **montar** la app, pero **no** es donde acaba el bucle `query`; eso ocurre en **`query.ts`** tras pasar por REPL.

---

## 5. Evidencia en código (fragmentos reales)

Ya citados arriba:

- Final de `cli.tsx` → import de `main.js` y `await cliMain()`.
- Inicio de `export async function main()` en `main.tsx` (líneas ~585+).
- `launchRepl` en `replLauncher.tsx`.
- `for await (const event of query({...}))` en `REPL.tsx`.
- `await handlePromptSubmit({ ... onQuery ... })` en `REPL.tsx`.
- `export async function* query` y `queryLoop` en `query.ts`.
- Rama `bridgeMain` en `cli.tsx` y `export async function bridgeMain` en `bridgeMain.ts`.

---

## Resumen ejecutivo

| Pregunta | Respuesta basada en código |
|----------|------------------------------|
| ¿Dónde **inicia** el sistema CLI interactivo? | **`src/entrypoints/cli.tsx`** → **`main.tsx#main()`**. |
| ¿Dónde entra el **input del usuario**? | **`src/screens/REPL.tsx`** (UI Ink / `PromptInput`), luego **`handlePromptSubmit`**. |
| ¿Dónde “**piensa**” y ejecuta **tools** en bucle? | **`src/query.ts`** (`query` / `queryLoop`), invocado desde REPL con `canUseTool` y `toolUseContext`. |
| ¿Qué es `bridgeMain`? | **Otro entry de ejecución** para modo bridge/remoto, no la ruta por defecto del TUI local. |

---

*Documento generado como auditoría estática; el orden exacto dentro de `queryLoop` (cada `yield`/continue) requiere seguimiento línea a línea en `query.ts` para casos límite.*
