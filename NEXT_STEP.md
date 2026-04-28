# NEXT_STEP — vision_rag

> Documento vivo. Reemplazar/actualizar al cambiar el siguiente paso.

**Fecha:** 2026-04-28 (cierre de sesión)
**Etapa vigente:** Tres hilos en paralelo, todos abiertos:
1. **Hilo principal (sin cambios):** validación humana del Excel v3 sobre 4 expedientes (86 comprobantes). **Fase NO cerrada** — pendiente revisión manual contra PDFs.
2. **Hilo PRE-PASO 4.5 (cerrado en código):** schema `expediente.v4` commiteado en `eda3f4d`. Piloto `DEBEDSAR2026-INT-0103251` regenerado a v4 con `ruc_receptor` poblado en 9/10, Excel dedicado validado contra JSON. Los otros 3 expedientes siguen en v3. Ver D-24.
3. **Hilo PASO 4.5 Fase 1 (cerrado en código + validado empíricamente):** motor determinista MVP commiteado en `df813e2`. **Primera corrida real ejecutada sobre el piloto v4** → `decision_global=REVISAR`, 9 hallazgos, idempotencia byte-a-byte confirmada. Suite 69/69 verde. Ver D-25 + adenda 2026-04-28 en [`CURRENT_STATE.md`](CURRENT_STATE.md).

---

## Estado del artefacto

- **Ruta Excel:** `data/piloto_ocr/metrics/validacion_expedientes.xlsx`
- **Hojas:** `resumen`, `comprobantes` (86 filas ordenadas por prioridad), `documentos`, `expedientes`, `errores`, `resolucion_ids`
- **Expedientes incluidos:** `DEBE2026-INT-0316916` (15), `DEBEDSAR2026-INT-0103251` (10), `DIED2026-INT-0250235` (29), `DIED2026-INT-0344746` (32)

### Distribución actual del estado_consistencia

| Estado | Cantidad | % |
|---|---|---|
| DIFERENCIA_CRITICA | 15 | 17.4% |
| DATOS_INSUFICIENTES | 55 | 64.0% |
| DIFERENCIA_LEVE | 1 | 1.2% |
| OK | 15 | 17.4% |

**Requieren revisión manual (`flag_revision_manual=SI`):** 70 de 86 (81.4%).

---

## Siguiente paso — VALIDACIÓN HUMANA DEL EXCEL

**La fase no se cierra con generación del Excel.** El Excel es entrada de trabajo, no salida final. El cierre de fase requiere decisión explícita de Hans tras revisión contra PDFs.

### Qué hacer

1. **Abrir** `data/piloto_ocr/metrics/validacion_expedientes.xlsx`.
2. **Leer** hoja `resumen` para contexto global.
3. **Filtrar** hoja `comprobantes` por `flag_revision_manual = SI` (70 filas).
4. **Revisar primero los 15 DIFERENCIA_CRITICA**:
   - Leer `detalle_inconsistencia` (explica qué componente falla).
   - Abrir el PDF correspondiente (`archivo` + `pagina_inicio`) y contrastar.
   - Llenar columnas humanas: `comentario_validacion`, `monto_correcto`, `ruc_correcto`, `proveedor_correcto`, `observaciones`, `validacion_final`.
5. **Luego los 55 DATOS_INSUFICIENTES**:
   - La mayoría son casos donde OCR no capturó el desglose tributario (Marcoantonio con columnas pegadas, boletas EB01 simplificadas, decimales truncados por OCR).
   - Completar lo que sea observable directamente del PDF y dejar trazabilidad en `observaciones`.
6. **Los 15 OK** — muestreo opcional; la suma de componentes ya cuadra ±1.00.

### Criterio de cierre de fase

La fase queda **cerrada** cuando:

- `validacion_final` llena para todos los comprobantes con `flag_revision_manual=SI`, o
- Hans decide explícitamente aceptar el Excel con lagunas conocidas y documenta la aceptación.

Mientras tanto, el estado operativo del proyecto es **"pipeline técnicamente estable + Excel listo para revisión; fase en curso, sin cierre"**.

### Qué NO hacer todavía

- **No iterar más OCR global** — el OCR agresivo ya corrió y alcanzó su techo (+4/59 recuperados, ~6.8%). Los 55 restantes no son recuperables solo con preprocesamiento global. Ver D-22.
- **No agregar más campos contables** (ISC, Otros Tributos, FISE, Monto de redondeo) hasta cerrar validación humana de esta fase. `recargo_consumo` ya está implementado y latente.
- **No abrir integración AG-EVIDENCE**.
- **No refactorizar el Excel** — el esquema actual (26 columnas) basta para validación humana.
- **No commitear el Excel automáticamente** — queda en estado provisional hasta autorización explícita de Hans (`EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`). Ver D-23.
- **No regenerar `expediente.json` ni Excel para migrar a v4 sin autorización** — el código PRE-PASO 4.5 está mergeado, pero los artefactos siguen en v3. La regeneración debe ser controlada (1 expediente piloto, comparación v3 vs v4) antes de tocar los 4 expedientes existentes. Ver siguiente sección y D-24.

---

## Hilo PRE-PASO 4.5 — regeneración controlada a `expediente.v4` (autorizable)

**Estado al 2026-04-27:** código mergeado en 5 commits. Sin ejecución de pipeline. Sin tests automáticos ejecutados. Sin artefactos regenerados.

### Próximo paso autorizable (no ejecutado todavía)

1. **Ejecutar la suite de tests sintéticos** añadida en PRE-PASO 4.5:
   - `pytest tests/test_consistencia_tributaria.py tests/test_consolidador_persistencia.py tests/test_idempotencia_consolidador.py -v`
   - Confirma que módulo puro, persistencia y idempotencia byte-a-byte pasan en este entorno.
2. **Elegir 1 expediente piloto** de los 4 actuales (sugerencia operativa: `DIED2026-INT-0344746` por tener la mayor cobertura de campos tributarios reales).
3. **Hacer backup** del JSON v3 actual (`control_previo/procesados/<id>/expediente.json` → copia con sufijo `.v3.bak`) **antes** de regenerar.
4. **Regenerar el JSON** del expediente piloto con `python scripts/consolidador.py` (o el comando equivalente que use `consolidar()` desde el CLI).
5. **Diff semántico** v3 vs v4:
   - `schema_version` debe pasar de `"expediente.v3"` a `"expediente.v4"`.
   - Cada `comprobante` debe ganar `ruc_receptor`, `estado_consistencia`, `tipo_tributario`, `detalle_inconsistencia`.
   - Los demás campos no deben cambiar (montos, RUC emisor, fechas, hashes).
6. **Regenerar Excel solo de ese expediente** con `python scripts/ingest_expedientes.py export --expediente-id <id>` (output local, no commit).
7. **Comparar Excel v3 vs Excel v4** sobre el mismo expediente piloto:
   - `estado_consistencia` y `tipo_tributario` deben coincidir fila por fila (la lógica es la misma, solo cambió el lugar donde se calcula).
   - Si no coincide → bug en `consistencia_tributaria.py` o en la propagación; bloqueante.
8. **Reportar diff** y esperar autorización para migrar los 3 expedientes restantes.

### Qué NO hacer en este hilo

- No regenerar los 4 expedientes en lote sin haber validado el piloto primero.
- No commitear el Excel v4 (sigue D-23).
- No tocar `decision_engine.py` ni introducir el motor PASO 4.5 todavía — eso requiere haber cerrado este hilo y pasar a Fase 1 con autorización separada.

---

## Hilo PASO 4.5 Fase 1 — validado empíricamente (cierre 2026-04-28)

Estado al cierre de sesión: motor implementado, tests 69/69 verdes, **primera corrida real ejecutada sobre el piloto v4**, idempotencia byte-a-byte confirmada empíricamente. Detalle completo en la adenda "Cierre de sesión 2026-04-28" de [`CURRENT_STATE.md`](CURRENT_STATE.md).

### Próximo paso recomendado para mañana — mini-demo técnica del PASO 4.5

Preparar una mini-demo reproducible para concurso/jueces que muestre el flujo end-to-end sobre el piloto:

1. **Suite verde**: `C:/Python314/python.exe -m pytest tests/ -v` → 69 PASSED.
2. **Mostrar `expediente.v4` real** del piloto: campos persistidos (`ruc_receptor`, `estado_consistencia`, `tipo_tributario`, `detalle_inconsistencia`).
3. **Ejecutar el motor en vivo** sobre el piloto: `python scripts/auditoria/decision_engine.py control_previo/procesados/DEBEDSAR2026-INT-0103251 --deterministico` → JSON a stdout.
4. **Mostrar `decision_global=REVISAR`** y los 9 hallazgos clasificados por regla.
5. **Demostrar idempotencia** corriendo el motor 2 veces y haciendo diff del payload determinista (sha256 byte-igual).
6. **Mostrar separación schema vs lógica**: `decision_engine.v1` desacoplado de `expediente.v4`; reglas atómicas auditables individualmente.

Material a preparar: guion + capturas + tiempos estimados. Sin código nuevo. Sin reglas nuevas. Sin IA. Solo lo ya entregado funcionando reproduciblemente.

### Alternativas (si la mini-demo no es prioritaria)

- **Migrar un segundo expediente a `expediente.v4`** (sugerido: `DIED2026-INT-0344746` por ser el de mayor cobertura tributaria) y correr el motor sobre él para diversificar la evidencia.
- **Crear exportador Excel para `decision_engine_output.json`** (visualización del veredicto del motor por revisor humano; complementario al Excel de comprobantes existente).
- **Diseñar capa IA explicadora** (no juez) que responda preguntas de jueces sobre los hallazgos, leyendo el `decision_engine_output.json` como contexto.

Cualquiera de las 3 alternativas requiere **autorización explícita por separado** y diseño previo antes de tocar código.

### Qué NO hacer todavía

- **No correr el motor sobre los otros 3 expedientes** sin migrarlos antes a `expediente.v4` (los rechazaría con `SchemaVersionError`).
- **No regenerar el Excel principal** `validacion_expedientes.xlsx` (ver D-23 sobre política de versionado).
- **No commitear el Excel piloto** `validacion_DEBEDSAR2026-INT-0103251_v4_piloto.xlsx`.
- **No introducir LLM como juez** (las reglas son deterministas por diseño; un LLM puede explicar pero no decidir).
- **No agregar reglas nuevas** (R-DUPLICADOS, R-MONTO-MAXIMO, R-FECHA-FUERA-DE-COMISION, etc.) antes de validar la demo y cerrar feedback.
- **No hacer push de artefactos** (Excel piloto, `decision_engine_output.json`, `*.bak`, PDFs, datos sensibles del expediente).
- **No integrar con `ingest_expedientes.py`** (subcomando `audit`) hasta haber visto el motor en una demo y recibir feedback.

---

## Criterio de salida de este paso

- Excel con todas las filas `flag_revision_manual=SI` revisadas contra PDF, columnas humanas llenas.
- Decisión explícita de Hans sobre: (a) aceptar el estado actual como "validado parcialmente", (b) exigir mejoras adicionales al pipeline, o (c) pasar a la siguiente fase del roadmap.

---

## Referencias rápidas

- Estado técnico completo: [`CURRENT_STATE.md`](CURRENT_STATE.md)
- Decisiones D-01…D-25: [`docs/DECISIONES_TECNICAS.md`](docs/DECISIONES_TECNICAS.md)
- Regenerar Excel localmente (no versionar): `python scripts/ingest_expedientes.py export`
- Reprocesar un expediente puntual: `python scripts/ingest_expedientes.py run-all --src <carpeta> --expediente-id <id>`
- **Política Excel**: el `.xlsx` NO se commitea automáticamente hasta que Hans autorice con frase equivalente a `EXCEL VALIDADO` / `AUTORIZADO PARA VERSIONAR`. Ver D-23.

---

*Al completar la validación humana, reemplazar este documento con el siguiente paso o archivarlo.*
