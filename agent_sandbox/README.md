# Agente sandbox (arquitectura por nodos)

Sistema **modular** con flujo fijo:

`input_node` → **(hasta 2×)** `reasoning_node` → `tool_node` → `validation_node` → `output_node`  
(si la validación falla con tool, se reintenta un ciclo de decisión sin segundo LLM).

Implementación en **Python estándar**, sin LangChain/LangGraph, pero con **estructura equivalente** a un grafo lineal fácil de portar.

## Estructura

| Archivo / carpeta | Rol |
|-------------------|-----|
| `state.py` | `AgentState` (dataclass inmutable vía `replace`) |
| `orchestrator.py` | `run_pipeline` (ciclo acotado reasoning→tool→validación, máx. 2) |
| `nodes/` | Un archivo por nodo (función pura `AgentState` → `AgentState`) |
| `tools.py` | Herramientas + `despachar` con contrato uniforme |
| `llm_client.py` | `analizar_con_llm` (OpenRouter o simulación por reglas sin API key) |
| `main.py` | CLI; solo delega en `run_pipeline` |

## Razonamiento con LLM

`analizar_con_llm` devuelve un `dict` con:

- `intencion`, `tool` (o `null` si no aplica), `confianza` (0–1), `fuente` (`llm`, `simulado`, `fallback_reglas`).

Con **`OPENROUTER_API_KEY`**, se llama al modelo con JSON estricto; se **valida** el nombre de `tool` contra la lista permitida y la **coherencia** básica con el texto del usuario. Si el JSON es inválido, la red falla o la **confianza es menor que 0.5**, se aplica **fallback a reglas** (trazable con `motivo_fallback` cuando aplica).

Sin clave, `fuente` = **simulado** (`analizar_por_reglas`).

## Estado (`AgentState`)

- `input_usuario`, `intencion`, `tool_seleccionado`, `resultado_tool`, `respuesta_final`, `historial`
- **`trazas_decision`**: tupla de dicts con eventos estructurados por paso (auditoría).
- Campos auxiliares: `validacion_ok`, `error_flujo` (p. ej. entrada vacía en `input_node`)

## Contrato de herramientas

Cada resultado es un `dict` con: `ok`, `tool`, `message`, `data`.

## Ejecución

```bash
cd agent_sandbox
python main.py
```

## Evolución

- Cambiar modelo (`OPENROUTER_MODEL`) o añadir caché en `llm_client` sin tocar nodos.
- Añadir ramas condicionales en el orquestador (o varios `PIPELINE`) como en LangGraph.
- Extender `validation_node` con reglas normativas (MINEDU).
