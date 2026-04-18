# NEXT_STEP — vision_rag

> Documento vivo. Reemplaza/actualiza al cambiar el siguiente paso.

**Fecha:** 2026-04-18
**Etapa vigente:** pipeline de comprobantes extendido con desglose tributario (`bi_gravado`, `op_exonerada`, `op_inafecta`) + `monto_total` / `monto_igv` con regex flexible. Etapa **NO cerrada**.

---

## Siguiente paso — VALIDACIÓN DE EXCEL

**No implementar nuevas features.** El foco es verificar que lo ya extraído es correcto.

### Qué validar

1. **Comparar contra archivo cowork**
   - Fuente externa: `DIED2026-INT-0344746_VIATICO_17_04_9.42am/COWORK_Comprobantes_0344746.xlsx`.
   - Pipeline: `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (regenerado para el expediente `DIED2026-INT-0344746`).
   - Comparar fila por fila: RUC, razón social, serie, fecha, monto_total, bi_gravado, monto_igv, op_exonerada, op_inafecta.

2. **Detectar discrepancias reales**
   - Montos distintos entre cowork y pipeline.
   - Comprobantes que cowork lista pero pipeline no detectó, o viceversa.
   - Proveedores mal normalizados.
   - Clasificar cada discrepancia: ¿error del OCR, error de regex, error de cowork humano, o diferencia de criterio?

3. **Confirmar cobertura de desglose tributario**
   - Los 16 casos con `op_exonerada` y 13 con `op_inafecta` detectados en `DIED-0344746`: verificar manualmente contra el PDF que los valores extraídos coinciden.
   - Casos con `0.00` legítimos (boletas SUNAT): confirmar que el renglón en el PDF realmente dice `S/ 0.00` y no un número distinto.
   - Los 2 casos con valor >0 en `op_exonerada` (p22=90.00, p126=100.00 ANFLOR): confirmar contra el PDF.

4. **Clasificar cada NULL residual** según la política D-14 (`docs/DECISIONES_TECNICAS.md`): `ausencia_estructural` | `fallo_ocr` | `gap_regex` | `decimales_sin_ancla`. No usar "sin dato" a secas — cada NULL debe tener categoría explicable.

### Qué NO hacer todavía

- **No agregar** nuevos campos (ISC, Otros Cargos, Otros Tributos, Redondeo, Valor FISE, etc.).
- **No tocar** regex de monto_total, IGV, bi_gravado, op_exonerada, op_inafecta (a menos que la validación revele un bug real, en cuyo caso reportar antes de cambiar).
- **No abrir** clasificador MEF / concepto presupuestal.
- **No integrar** con AG-EVIDENCE ni con el agente normativo.

### Criterio de salida de este paso

- Evidencia tabular (Excel o reporte) de concordancia pipeline vs cowork en `DIED2026-INT-0344746`.
- Lista cerrada de discrepancias con categoría asignada.
- Decisión explícita de Hans sobre qué hacer con cada discrepancia (fix, ignorar, escalar).

---

## Referencias rápidas

- Estado técnico completo: [`CURRENT_STATE.md`](CURRENT_STATE.md)
- Handoff de cierre determinista previo: `HANDOFF_FINAL_ETAPA_DETERMINISTA.txt`
- Roadmap PASO 0–7: `docs/ROADMAP_PROYECTO.md`
- Comandos pipeline:
  ```
  python scripts/ingest_expedientes.py run-all --src <carpeta> --expediente-id <id>
  python scripts/ingest_expedientes.py export --expediente-id <id>
  ```
- Ruta Excel: `data/piloto_ocr/metrics/validacion_expedientes.xlsx` (hoja `comprobantes`).

---

*Al completar la validación de Excel, reemplazar este documento con el siguiente paso o archivarlo.*
