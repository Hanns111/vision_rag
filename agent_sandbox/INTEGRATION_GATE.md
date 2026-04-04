# Puerta de integración (Integration Gate)

Checklist orientado a **auditoría** y a decisión documentada. Aplicable cuando se evalúe llevar un componente o patrón desde **agent_sandbox** hacia **AG-EVIDENCE**. Este archivo no modifica código productivo; solo define el umbral de aceptación.

**Regla de oro:** ningún componente del sandbox pasa sin cumplir **todos** los ítems verificables de la sección obligatoria.

---

## Resumen de criterios

La integración exige demostración verificable de:

1. Citas normativas reales (artículo, numeral, inciso) donde el producto las requiera.  
2. Fuente verificable (archivo + página o equivalente productivo).  
3. Ausencia de alucinación en batería de pruebas controladas.  
4. Trazabilidad completa del origen de cada fragmento relevante.  
5. Estabilidad de comportamiento bajo criterios acordados.  
6. Validación frente a **golden dataset** con métricas y umbrales documentados.

Detalle normativo y contexto: `RELATION_TO_AG_EVIDENCE.md` (sección *CRITERIOS DE INTEGRACIÓN FUTURA*).

---

## Checklist de validación (sí / no + evidencia)

Registrar para cada ítem: **cumple (S/N)**, **referencia de evidencia** (enlace a informe, commit, tabla de resultados, ID de ejecución de pruebas), **responsable / fecha de registro** según el proceso interno del equipo (sin fijar calendario en este documento).

| # | Criterio | ¿Cumple? | Evidencia (obligatorio si Sí) |
|---|----------|----------|------------------------------|
| G1 | Citas normativas reales: artículo, numeral, inciso (según especificación productiva) | | |
| G2 | Fuente verificable: archivo + página (o equivalente aceptado en AG-EVIDENCE) | | |
| G3 | Pruebas controladas de alucinación: escenarios y umbral definidos; resultados archivados | | |
| G4 | Trazabilidad: procedencia de cada fragmento (pipeline, versión de índice/corpus) | | |
| G5 | Estabilidad: criterios de variación aceptable documentados y medidos | | |
| G6 | Golden dataset: conjunto, métricas, umbral de pase; resultado verificable | | |

### Bloqueos explícitos

- Si cualquier fila **G1–G6** está en **No** sin plan de remediación aprobado → **no integrar**.  
- Si la evidencia no es localizable por auditoría → tratar como **No cumplido**.

### Forma aceptable de integración (recordatorio)

- Migración revisada de ideas o componentes, **adaptación** al pipeline productivo, **validación** en el entorno real de AG-EVIDENCE.  
- **Prohibido:** copia directa sin revisión, acoplamiento de repositorios, o ejecución unificada impuesta desde el sandbox.

---

## Referencias en este repositorio

- `ARCHITECTURE.md` — propósito del sandbox y reglas de desacoplamiento.  
- `RELATION_TO_AG_EVIDENCE.md` — qué se comparte, qué no, y criterios de integración futura.
