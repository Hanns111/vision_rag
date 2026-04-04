# Relación entre agent_sandbox y AG-EVIDENCE

Documento de gobernanza y límites. **Ámbito:** describe la relación **conceptual** entre el laboratorio local `agent_sandbox` y el sistema productivo **AG-EVIDENCE**. No accede a código ni infraestructura de AG-EVIDENCE.

---

## Qué comparte

| Dimensión | Descripción |
|-----------|-------------|
| **Objetivos** | Interés común en **RAG normativo confiable**: recuperación útil, citas cuando aplique, minimización de afirmaciones sin soporte documental. |
| **Enfoque** | **Auditabilidad:** trazas y criterios explícitos para reconstruir qué se hizo y con qué evidencia. |
| **Principios** | **Evidencia y trazabilidad** por encima de la inferencia libre; verificabilidad donde el dominio lo demande. |

Todo lo anterior es **conocimiento validado** y **política**, no artefactos ejecutables compartidos.

---

## Qué NO comparte

| Dimensión | Descripción |
|-----------|-------------|
| **Código** | Repositorios y módulos independientes. Sin dependencias cruzadas impuestas desde este sandbox. |
| **Dependencias** | No se declaran ni se exige alinear `requirements` ni stacks entre proyectos. |
| **Ejecución** | Procesos, contenedores, jobs y entornos separados. |
| **Infraestructura** | Red, almacenamiento productivo, secretos y despliegues de AG-EVIDENCE no son utilizados ni referenciados operativamente desde aquí. |

---

## Estado actual

| Entorno | Rol |
|---------|-----|
| **agent_sandbox** | **En desarrollo / laboratorio:** experimentation, índices locales, agente modular, criterios de confianza documentados en código y MD. |
| **AG-EVIDENCE** | **Productivo:** sistema principal, crítico y gobernado fuera de este árbol de archivos. |

No hay integración directa en el momento descrito por esta documentación.

---

## CRITERIOS DE INTEGRACIÓN FUTURA

### Definición

La integración **no** ocurre por decisión manual arbitraria ni por conveniencia de despliegue. Solo puede considerarse cuando se cumplen **condiciones verificables** y queda registro de la evidencia de cumplimiento (auditoría).

Hasta entonces, los sistemas permanecen **desacoplados**.

### Condiciones obligatorias

Las siguientes condiciones deben poder **comprobarse** con artefactos de prueba, registros y, donde aplique, conjunto de referencia:

1. **Respuestas con citas normativas reales** (cuando el producto las exija), incluyendo resolución explícita de:
   - artículo  
   - numeral  
   - inciso  

2. **Fuente verificable** para fragmentos citados o usados como evidencia:
   - archivo (identificador estable acordado en el sistema productivo)  
   - página (o equivalente aceptado en el pipeline productivo)  

3. **Cero alucinaciones en pruebas controladas:** conjunto de escenarios definidos donde la salida se contrasta con fuentes; tasas y criterios de fallo acordados para el producto.

4. **Trazabilidad completa** del origen de cada fragmento relevante:
   - cómo se obtuvo (recuperación, rerank, filtros)  
   - qué versión de índice o corpus aplicó  

5. **Comportamiento estable:** repeticiones y variaciones acotadas según umbrales definidos; sin degradaciones no explicadas entre evaluaciones.

6. **Validación contra golden dataset:** conjunto de referencia acordado; métricas y umbral de aceptación documentados para el tránsito a producción.

### Regla de oro

> **Ningún componente del sandbox se integra en AG-EVIDENCE sin cumplir todos los criterios anteriores.**

La ausencia de cualquiera de ellos es **bloqueo** hasta su resolución documentada.

### Forma de integración (conceptual)

- **Migración de componentes**, no copia directa de archivos sin revisión.  
- **Adaptación al pipeline existente** de AG-EVIDENCE (interfaces, políticas, seguridad).  
- **Validación dentro del sistema real** (entornos y pruebas propios del producto).

No se definen en este documento plazos, roadmap ni tareas técnicas concretas de integración; solo **condiciones objetivas** y el marco de auditoría.

---

*Para checklist operativo resumido, ver `INTEGRATION_GATE.md`.*
