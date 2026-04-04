# Diagrama de flujo del agente (abstracto)

Solo arquitectura. Sin rutas de archivos ni código.

---

## Vista lineal principal (TUI interactiva)

```mermaid
flowchart LR
  subgraph CLI["Capa CLI"]
    A[Entrada bootstrap]
  end
  subgraph MAIN["Núcleo aplicación"]
    B[Init global y rutas]
  end
  subgraph TUI["Sesión interactiva"]
    C[REPL / UI]
  end
  subgraph SUBMIT["Orquestación de prompt"]
    D[handlePromptSubmit]
  end
  subgraph ENGINE["Motor de turno"]
    E[query]
    F[queryLoop]
  end
  subgraph FX["Efectos"]
    G[Tools]
    H[Servicios API modelo]
  end
  subgraph OUT["Salida"]
    I[Eventos a UI / transcript]
  end

  A --> B
  B --> C
  C --> D
  D --> E
  E --> F
  F --> H
  F --> G
  G --> F
  H --> F
  F --> I
  I --> C
```

Interpretación:

- **CLI → MAIN:** arranque y decisión de modo.
- **MAIN → REPL:** montaje de la sesión visible.
- **REPL → QUERY:** cada envío serio de input pasa por orquestación de submit y entra al motor.
- **QUERY / queryLoop:** puede alternar entre razonamiento vía API y ejecución de **TOOL** hasta cerrar el turno.
- **RESPONSE:** eventos y mensajes vuelven a la REPL (y equivalen a “respuesta” al usuario).

---

## Cadena corta (resumen)

```
CLI → MAIN → REPL → QUERY → TOOL → RESPONSE
```

En la práctica, **RESPONSE** es un flujo de eventos que **alimenta de nuevo** la REPL hasta el siguiente input.

---

## Variante conceptual: solo lectura mental

```
Usuario
  → CLI (argv)
  → MAIN (config)
  → REPL (input visual)
  → SUBMIT (semántica del enter)
  → QUERY LOOP (modelo ↔ herramientas)
  → API + TOOLS
  → REPL (output)
```
