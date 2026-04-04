# Blueprint del agente (vista abstracta)

Documento **solo de arquitectura**: no incluye código ni rutas de proyecto. Sirve para replicar el diseño en otro stack (por ejemplo MINEDU o LangGraph).

---

## Flujo extremo a extremo

```
Usuario (terminal)
    → Entrada CLI (bootstrap + argumentos)
    → Núcleo de aplicación (orquestación global, flags, init)
    → Lanzador de sesión interactiva (TUI)
    → Capa REPL (lectura de input, estado de mensajes, UI)
    → Envío de prompt (orquestador de submit: colas, comandos, permisos previos)
    → Motor de consulta (generador async: un “turno” del agente)
    → Bucle interno del turno (mensajes, herramientas, compactación, reintentos)
    → Herramientas (ejecución + resultados)
    → Respuesta / streaming de eventos hacia la UI
    → Usuario ve el output
```

Forma compacta alineada con el análisis de referencia:

**input → REPL → handlePromptSubmit → query → queryLoop → tools → output**

---

## Componentes

### 1. Entrada (CLI)

- **Rol:** primer proceso lógico; discrimina modos (versión, subcomandos, bridge, impresión headless, etc.).
- **Salida típica:** invocar el “núcleo de aplicación” del producto interactivo o delegar en otro binario de servicio.

### 2. Núcleo de aplicación (main)

- **Rol:** configuración global, políticas, telemetría, parsing de CLI, preparación del entorno.
- **Salida típica:** arrancar la TUI con un componente REPL embebido en el árbol de la app.

### 3. UI (REPL)

- **Rol:** captura input del usuario; muestra historial, permisos, progreso y resultados.
- **Responsabilidades:** estado de mensajes, callbacks de submit, enlace con sesión y modelo.

### 4. Orquestador de submit (`handlePromptSubmit`, conceptual)

- **Rol:** traducir un “enter” en el input a una acción coherente: comando slash, cola, validaciones, hooks de inicio de sesión.
- **Salida típica:** invocar el callback que dispara el **motor de consulta** con mensajes y contexto listos.

### 5. Loop (motor `query` / `queryLoop`)

- **Rol:** un **turno** puede implicar varias iteraciones internas (modelo → posible uso de herramienta → resultado → siguiente mensaje del modelo).
- **Entradas conceptuales:** historial de mensajes, system prompt efectivo, contexto de usuario/sistema, política de uso de herramientas (`canUseTool`), contexto de herramientas.
- **Salida:** stream de eventos (tokens, bloques de herramienta, mensajes persistidos, errores, compactaciones).

### 6. Tools

- **Rol:** ejecutar acciones concretas (archivo, shell, agente hijo, MCP, etc.) y devolver resultados al historial.
- **Acoplamiento:** nombradas y resueltas desde el motor de consulta; permisos mediados por capas superiores.

### 7. Servicios API

- **Rol:** llamadas al proveedor del modelo, refresco de tokens, reintentos, límites y errores de red.
- **No** son el “cerebro” de orquestación: alimentan al motor de consulta.

---

## Separación de responsabilidades

| Capa | Pregunta que responde |
|------|------------------------|
| CLI | ¿Cómo arranca el binario y qué modo corre? |
| Main | ¿Qué política y configuración global aplica antes de la sesión? |
| REPL | ¿Cómo interactúa el humano con el sistema? |
| Submit | ¿Qué hace exactamente esta línea de input (comando vs prompt vs cola)? |
| Query / queryLoop | ¿Cómo se cierra un turno con modelo + herramientas? |
| Tools | ¿Qué efectos secundarios están permitidos? |
| API | ¿Cómo hablo con el modelo remoto? |

---

## Notas para reimplementación

- El diseño es **reactivo por eventos** en la UI y **asíncrono por generadores** en el motor de consulta.
- La **seguridad y gobernanza** (políticas, permisos) atraviesan varias capas; un blueprint mínimo puede modelarlas como un solo “policy gate” ante `tool_node`.
- Modos alternativos (bridge remoto, impresión sin TUI) son **grafos de arranque distintos**; el flujo anterior describe el **camino interactivo estándar**.
