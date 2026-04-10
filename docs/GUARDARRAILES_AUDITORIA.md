# Guardarraíles de auditoría — expedientes de control previo

> **Alcance:** revisión documental y validación de gasto sobre expedientes bajo `control_previo/` (viáticos, OS/OC, caja chica, etc.).  
> **Fuera de alcance inmediato:** línea subvención FONDEP (`06_subvenciones/`) salvo que un documento aparte extienda reglas específicas.  
> **Relación con piloto OCR:** el PASO 0 en `data/piloto_ocr/` mide extracción de campos; **no** sustituye este guardarraíl ni valida identidad de expediente por sí solo.

**Actualizado:** 2026-04-09

---

## 1. Principio obligatorio

Antes de cualquier **revisión documental** o **validación de gasto**, debe validarse primero la **identidad única del expediente** mediante el conjunto mínimo **EXPEDIENTE_ID** (§2) y las reglas (§3).

Sin esa validación **no** se declara el expediente como válido ni se asume coherencia entre piezas documentales.

---

## 2. EXPEDIENTE_ID (base mínima)

Campos de referencia que deben ser **coherentes** entre sí y entre los documentos del mismo expediente:

| Campo | Descripción operativa |
|-------|------------------------|
| **comisionado** | Persona o identificación del comisionado asociado al trámite. |
| **nro_planilla** | Número de planilla de viáticos (u homólogo según trámite). |
| **nro_siaf / pedido** | Referencia SIAF y/o pedido según el formato institucional vigente. |
| **destino** | Destino declarado del viaje o comisión. |
| **rango_fechas** | Rango de fechas de la comisión o del período relevante. |

La extracción concreta de valores (OCR, lectura manual, etc.) es **posterior** a la definición de este marco; el guardarraíl exige **cruce** explícito, no solo lectura aislada por documento.

---

## 3. Reglas obligatorias

1. **Coincidencia con EXPEDIENTE_ID**  
   Si un documento **no** puede alinearse con el **EXPEDIENTE_ID** acordado para el expediente en curso → se **bloquea** el análisis de ese documento como parte del **mismo** expediente hasta aclarar origen o descartar inclusión.

2. **Mezcla de expedientes (error grave)**  
   Si coexisten **múltiples valores incompatibles** en **comisionado**, **nro_planilla** o **destino** entre documentos que se pretendían del mismo lote → **ERROR GRAVE: MEZCLA DE EXPEDIENTES**. No procede validar gasto ni cerrar revisión.

3. **Validación cruzada**  
   Debe existir **validación cruzada** entre, como mínimo: **planilla**, **solicitud**, **anexo 3**, **declaración jurada (DJ)** y **comprobantes** de pago, en la medida en que figuren en el expediente.

4. **Contexto geográfico**  
   Debe existir **validación de contexto geográfico** (coherencia destino / itinerario / comprobantes según el caso).

5. **Prohibición de cierre inválido**  
   Si **alguna** validación obligatoria **falla**, queda **prohibido** declarar el expediente como **válido**.

---

## 4. Check final (antes de concluir)

Antes de dar por cerrada una revisión o validación de gasto, debe emitirse explícitamente:

| Pregunta | Respuesta permitida |
|----------|------------------------|
| ¿Expediente único? | **SI** / **NO** |
| ¿Coherencia total? | **SI** / **NO** |
| ¿Riesgo de error? | **ALTO** / **MEDIO** / **BAJO** |

Si **Expediente único** o **Coherencia total** es **NO**, o el **riesgo** es **ALTO** sin mitigación documentada, no se declara el expediente válido (§3.5).

---

## 5. Integridad de ubicación en el repositorio

Los expedientes de evidencia deben residir bajo la taxonomía de `control_previo/` (p. ej. `control_previo/01_viaticos/expedientes_revision/<ID_expediente>/`), no como carpetas sueltas en la raíz del repositorio. Véase `control_previo/README.md`.

---

## 6. Referencias

| Documento | Contenido |
|-----------|-----------|
| `docs/DECISIONES_TECNICAS.md` | Decisión **D-10** (adopción de este guardarraíl). |
| `docs/CONTROL_PREVIO_TAXONOMIA_EXPEDIENTES.md` | Taxonomía por categoría MINEDU. |
| `control_previo/README.md` | Estructura `normativa/` + `expedientes_revision/`. |
