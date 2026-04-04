# Arquitectura: agent_sandbox (SANTO GRIAL)

Documento técnico de contexto. **Ámbito:** únicamente el entorno experimental `agent_sandbox` bajo el proyecto de trabajo local (SANTO GRIAL). No describe ni modifica sistemas externos.

## 1. Propósito del sandbox

- **Entorno experimental controlado:** aquí se prueban patrones de RAG normativo, recuperación híbrida, índices en disco, trazas de decisión y logging, sin comprometer un sistema productivo.
- **Validación de componentes antes de producción:** los resultados se evalúan contra criterios explícitos (documentados en `RELATION_TO_AG_EVIDENCE.md` e `INTEGRATION_GATE.md`) antes de considerar cualquier uso fuera del laboratorio.
- **Desarrollo iterativo sin afectar el sistema real:** no hay acoplamiento de ejecución, código compartido ni dependencias con el sistema productivo **AG-EVIDENCE**. Lo reversible y lo fallible ocurre acá.

## 2. Relación con AG-EVIDENCE

- **AG-EVIDENCE** es el **sistema productivo**: crítico, gobernado y operado bajo sus propias reglas y repositorio. Este documento **no** lo modifica ni lo accede.
- **agent_sandbox** es el **entorno de laboratorio** del ecosistema de trabajo del equipo (conceptualmente bajo SANTO GRIAL / carpeta del proyecto local).
- **No existe integración directa** entre ambos en el estado descrito por esta documentación: no hay import de código cruzado, no pipeline único, no despliegue conjunto.

## 3. Principios compartidos (solo a nivel de criterio de diseño)

Ambos contextos pueden alinearse en **intención**, no en implementación:

- **Cero alucinación** como objetivo de diseño: recuperación fundamentada, citas cuando el producto lo exija, límites claros de lo que el modelo puede afirmar sin evidencia.
- **Trazabilidad:** registro de decisiones, fuentes y pasos reproducibles donde el producto lo defina.
- **Evidencia sobre inferencia:** priorizar fragmentos y metadatos verificables frente a conclusiones no ancladas.
- **Respuestas verificables** cuando el dominio (p. ej. normativo) lo exija: anclaje a texto y metadatos de fuente según las reglas del sistema que las implemente.

Estos principios se comparten como **conocimiento y política**, no como bibliotecas ni binarios.

## 4. Principios NO compartidos

De forma explícita, entre sandbox y AG-EVIDENCE **no** se comparten:

| Ámbito | Motivo |
|--------|--------|
| **Código** | Evitar acoplamiento y fugas de comportamiento no gobernado. |
| **Pipelines** | Cada sistema tiene su orquestación y sus controles propios. |
| **Ejecución** | Sin runtime compartido, sin servicios unificados impuestos desde el sandbox. |
| **Decisiones automáticas productivas** | El sandbox no toma decisiones en nombre del sistema productivo. |

## 5. Regla crítica

**Ningún componente del sandbox puede integrarse en AG-EVIDENCE sin validación completa** según los criterios verificables definidos en `RELATION_TO_AG_EVIDENCE.md` (sección de integración futura) y el checklist de `INTEGRATION_GATE.md`.

La integración conceptual es **migración y adaptación**, no copia directa ni activación automática.

---

*Última alineación documental con el código del sandbox: mantener coherencia revisando los módulos `pdf_rag.py`, `tools.py`, nodos y logging solo dentro de este repositorio.*
