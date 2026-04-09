# Puerta de entrada — referencia reconstruida (análisis del producto tipo “Claude Code”)

> **2026-04:** La carpeta grande de análisis **`SANTO_GRIAL_ANALYSIS/`** en la raíz del repo **puede haber sido eliminada** del disco local (no aportaba al pipeline de `agent_sandbox/`). Los enlaces relativos a `../../SANTO_GRIAL_ANALYSIS/` en este árbol quedan como **referencia histórica**; si necesitas ese material, recupera desde copia de seguridad.

**Importante:** El trabajo de “toda la noche” y los **gigabytes de material reconstruido** vivían principalmente en la carpeta hermana del repo:

**`SANTO_GRIAL_ANALYSIS/`** (raíz del proyecto)

Desde esta ubicación (`agent_sandbox/CLAUDE_CODE_SOURCE_REFERENCE/`), ruta relativa típica:

**`../../SANTO_GRIAL_ANALYSIS/`**

Esta carpeta (`CLAUDE_CODE_SOURCE_REFERENCE`) es el **mostrador ordenado**: reglas de aislamiento, índice maestro, síntesis de claves y copia del sandbox para auditores — **sin sustituir** el árbol de análisis si aún existe.

---

## Qué abrir primero (orden recomendado)

| Orden | Archivo | Para qué |
|------|---------|----------|
| 1 | [`INDICE_MAESTRO.md`](INDICE_MAESTRO.md) | Mapa de **todo** lo que generó el pipeline (carpetas, conteos, enlaces). |
| 2 | [`CLAVES_REINGENIERIA_SINTESIS.md`](CLAVES_REINGENIERIA_SINTESIS.md) | **Claves de arquitectura** en una sola lectura (flujo, archivos ancla, loop agente, LangGraph). |
| 3 | `../../SANTO_GRIAL_ANALYSIS/REPORTE_FINAL.md` | Totales verificados (output, índice, núcleo consolidado). |
| 4 | `../../SANTO_GRIAL_ANALYSIS/SYSTEM_BRAIN_CONFIRMED.md` | Cadena de llamadas **confirmada** en código reconstruido (cli → main → REPL → query). |
| 5 | `../../SANTO_GRIAL_ANALYSIS/SYSTEM_BLUEPRINT/` | Blueprint abstracto + diagramas + mapeo LangGraph. |

---

## Reglas de aislamiento (sistema ejecutable)

- El código bajo `SANTO_GRIAL_ANALYSIS/output/` y derivados es **referencia / análisis**, no el pipeline de **`agent_sandbox`** ni AG-EVIDENCE.
- **No ejecutes** ese árbol como si fuera tu agente de producción sin revisión.
- **No importes** rutas cruzadas desde `agent_sandbox/*.py` hacia `output/src` sin un diseño explícito.
- Cualquier producto “inspirado” en este análisis debe ser **reinterpretación propia**, no copia literal de binarios ni de material con licencia ajena.

---

## Subcarpetas aquí

| Carpeta | Contenido |
|---------|-----------|
| **`AGENT_SANDBOX_SOURCE_FOR_AUDIT/`** | Copia del **tu** código Python del sandbox + `README_AUDITORIA.md` para ChatGPT / auditores. |

---

## Aviso legal / honestidad intelectual

Este material documenta **arquitectura inferida a partir de artefactos de análisis** (p. ej. source maps y árbol reconstruido). **No** es el código fuente oficial del producto comercial, **no** “desbloquea” licencias ni sustituye documentación del fabricante, y **no** garantiza completitud del volumen total analizado (usa `INDICE_MAESTRO.md` y `PROJECT_INDEX.json` para cobertura).

---

## Empaquetado para ChatGPT (recomendado)

**Zip con casi todo el análisis + texto consolidado + sandbox Python:**  
**`../../CONSOLIDADO_PARA_COMPARTIR/SANTO_GRIAL_PARA_CHATGPT.zip`** (~30 MB típico).  
Instrucciones: **`../../CONSOLIDADO_PARA_COMPARTIR/INSTRUCCIONES_CHATGPT.md`**. Regenerar: **`empaquetar_para_chatgpt.ps1`** en esa carpeta.

Solo Markdown (sin zip): **`../../CONSOLIDADO_PARA_COMPARTIR/SANTO_GRIAL_TODO_EN_UNO.md`**.
