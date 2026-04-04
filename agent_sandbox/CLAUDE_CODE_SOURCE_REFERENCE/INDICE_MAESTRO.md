# Índice maestro — `SANTO_GRIAL_ANALYSIS`

Ruta absoluta típica: `…/SANTO GRIAL/SANTO_GRIAL_ANALYSIS/`  
Desde este archivo: **`../../SANTO_GRIAL_ANALYSIS/`**

---

## Pipeline documentado (`REPORTE_FINAL.md`)

| Script / artefacto | Rol |
|--------------------|-----|
| `proyecto.map` | Source map de entrada |
| `extract.js` | Extracción → `./output/` |
| `index-project.js` | Índice + JSON + grafos |
| `detect-brain.js` | Genera `SYSTEM_BRAIN.md` |
| `consolidate.js` | Núcleo priorizado → `CODIGO_FUENTE_RECONSTRUIDO/` |
| `verify.js` | Checklist |
| `run-pipeline.js` | Secuencia completa |

Ejecución: `node run-pipeline.js` (desde `SANTO_GRIAL_ANALYSIS`).

---

## Carpetas principales (referencia de volumen — ver `REPORTE_FINAL.md` para cifras exactas de tu última corrida)

| Carpeta / archivo | Contenido |
|-------------------|-----------|
| **`output/`** | Árbol **completo** reconstruido desde el map (miles de archivos; p. ej. ~4756 en una ejecución citada). |
| **`output/src/`** | Código fuente efectivo analizado en `SYSTEM_BRAIN_CONFIRMED.md`. |
| **`CODIGO_FUENTE_RECONSTRUIDO/`** | Subconjunto **priorizado** (~90 archivos en corrida citada): agents, tools, policy, prompts, alto `weight_score`, cerebro candidato + dependencias. Lista: **`_MANIFEST.json`**. |
| **`SOURCE_CODE_REFERENCE/`** | Referencia paralela con su `_MANIFEST.json` (ver repo). |
| **`PROJECT_INDEX.json`** | Índice masivo del proyecto (símbolos, rutas, dependencias). |
| **`PROJECT_TREE.md`** | Árbol legible. |
| **`DEPENDENCY_GRAPH.md`** | Grafo de dependencias. |
| **`SYSTEM_BRAIN.md`** | Candidato a “cerebro” por heurística de score. |
| **`SYSTEM_BRAIN_CONFIRMED.md`** | Cadena de arranque y loop **confirmada** en código. |
| **`REPORTE_FINAL.md`** | Resumen ejecutivo del pipeline y totales. |
| **`SYSTEM_BLUEPRINT/AGENT_BLUEPRINT.md`** | Vista abstracta e2e (CLI → REPL → query → tools). |
| **`SYSTEM_BLUEPRINT/AGENT_FLOW_DIAGRAM.md`** | Diagrama de flujo. |
| **`SYSTEM_BLUEPRINT/AGENT_PSEUDOCODE.md`** | Pseudocódigo. |
| **`SYSTEM_BLUEPRINT/LANGGRAPH_MAPPING.md`** | Mapeo a nodos tipo LangGraph (`input` → `reasoning` → `tool` → `validation` → `output`). |

---

## Dónde está “el grueso” de los ~GB

- En **`output/`** (y en el map / binarios originales que usaste como entrada, **fuera** de este listado si los guardaste en otro disco).
- Este índice **no duplica** esos bytes: solo **apunta** a ellos.

---

## Relación con esta carpeta `CLAUDE_CODE_SOURCE_REFERENCE`

| Aquí | Allá |
|------|------|
| Reglas de aislamiento y auditoría | Corpus técnico completo del análisis |
| `CLAVES_REINGENIERIA_SINTESIS.md` | Condensado de `SYSTEM_*` + `SYSTEM_BLUEPRINT/*` |
| `AGENT_SANDBOX_SOURCE_FOR_AUDIT/` | **Tu** sandbox Python (no es el TS del análisis) |
