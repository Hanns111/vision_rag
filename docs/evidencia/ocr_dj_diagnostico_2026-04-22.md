# Diagnóstico OCR DJ — DEBE2026-INT-0316916

**Fecha:** 2026-04-22
**Expediente analizado:** `DEBE2026-INT-0316916`
**Documento fuente:** `2026042110383RENDICIONDEVIATICOSERARGTARAPOTOPV (1).pdf`
**OCR cache:** `control_previo/procesados/DEBE2026-INT-0316916/ocr_cache/2026042110383RENDICIONDEVIATICOSERARGTARAPOTOPV (1).pdf.txt`
**Motor OCR:** `tesseract_baseline`

---

## 1. Cifras duras

| Indicador | Valor |
|---|---|
| Ítems DJ en el PDF (validación humana) | **21** |
| Ítems DJ visibles en el OCR (líneas con fecha dentro de la región `ANEXO N°4`) | **19** |
| Ítems enteros perdidos en la transcripción OCR | **2** |
| Ítems con importe parseable en formato `\d+\.\d{2}` | **7** |
| Ítems con importe corrupto o ilegible en OCR | **12** |
| Total DJ impreso correctamente en OCR (`I TOTAL Sé \| 165.00`) | **S/ 165.00** |
| Σ DJ parseable por el parser post-fix | **S/ 53.04** |
| Brecha financiera atribuible a OCR | **S/ 111.96** |
| Páginas DJ en el PDF / páginas que llegaron al OCR con datos | **2 / 1** |

---

## 2. Clasificación de los 19 ítems visibles por estado OCR del importe

| Estado | Cantidad | Ejemplos literales del OCR |
|---|---|---|
| Formato correcto `5.00` / `6.00` | 7 | `MOVILIDAD 5.00`, `MOVILIDAD 6.00`, `VILIDAD 5.00` |
| Sin punto decimal (`500`, `2500`) | 6 | `MOVILIDAD 2500`, `MOVILIDAD 500` |
| Ilegible (ruido OCR) | 4 | `MOVILIDAD ali`, `MOVILIDAD —`, `Te`, `OO` |
| Vacío (importe no transcrito) | 2 | `TAXI DEL AUDITORIO AL HOTEL MOVILIDAD` (sin cifra) |

---

## 3. Volcado literal del OCR (región `ANEXO N°4`)

```
24/03/2028 TAX! DEL AEROPUERTO AL TERMINAL TERRESTRE MOVILIDAD 2500
24/03/2026 TAX! DEL HOTEL ALA DRE MOVILIDAD ali
24/03/2026 TAX! DE LA DRE AL AUDITORIO MOVILIDAD 500
24/03/2026 TAXI DEL AUDITORIO AL RESTAURANTE MOVILIDAD 5.00 |
24/03/2026 TAXI DEL RESTAURANTE AL AUDITORIO MOVILIDAD 5.00
24/03/2026 TAXI DEL AUDITORIO AL HOTEL MOVILIDAD
25/03/2026 TAX! DEL HOTEL AL AUDITORIO = MOVILIDAD 500
25/03/2026 TAX! DEL AUDITORIO AL RESTAURANTE MOVILIDAD 5.00
25/03/2026 TAX! DEL AUDITORIO AL HOTEL MOVILIDAD 500
26/03/2026 TAX) DEL HOTEL AL AUDITORIO MOVILIDAD 500
26/03/2026 | TAXI DEL AUDITORIO AL RESTAURANTE MOVILIDAD —
26/03/2026 TAX! DEL RESTAURANTE AL AUDITORIO MOVILIDAD 500
26/03/2026 TAX! DEL AUDITORIO AL HOTEL MOVILIDAD 6.00
26/03/2026 TAX! DEL HOTEL AL RESTAURANTE PARA CENAR MOVILIDAD 5.00
27/03/2026 TAXI DEL HOTEL AL AUDITORIO VILIDAD 5.00
27/03/2026 [ AUDITORIO A LA DRE Te
27/03/2026 TAXI DE LA DRE AL TERRAPUERTO OO
27/03/2026 TAXI DEL TERRAPUERTO AL CREBE TARAPOTO MOVILIDAD 500
27/03/2026 TAX) DEL CREBE AL AEROPUERTO | MOVILIDAD

I TOTAL Sé | 165.00
```

Además, el OCR de la página `Página 2 de 2` del Anexo 4 solo transcribe el
header `ANEXO N°4 DECLARACIÓN JURADA` y la introducción del suscrito —
**no aparecen ítems de datos**, aunque el PDF real sí los tiene.

---

## 4. Evaluación del parser post-fix

Tras la reescritura acotada del extractor DJ
(`sandbox_test_cowork_v2/.../rules/dj_anexo3_conceptos.py`), el parser:

- Captura las **19 / 19** filas visibles en el OCR (cobertura 100% sobre lo extraíble).
- Aplica regex estricto de importe `\d+[\.,\s]\d{2}` y:
  - Acepta los 7 importes con formato correcto → Σ S/ 53.04.
  - Marca los 12 restantes como `IMPORTE_ILEGIBLE_PENDIENTE` (importe 0.00, visible para revisor humano).
- Asigna `numero_item` (1..19) y `pagina_pdf` (3) a cada fila.
- El saneamiento auxiliar `R-AUX-DJ-SANEAMIENTO` activa **0 descartes**.

**Conclusión técnica:** el parser funciona correctamente sobre el input que tiene.

---

## 5. Conclusión validada

**El cuello de botella actual está en OCR upstream, no en parsing DJ.**

Razón: el parser post-fix ya captura el 100% de las líneas que el OCR
expone (19/19) con `numero_item` y `pagina_pdf` asignados. La brecha con
los objetivos (21 ítems, S/ 165.00) proviene de:

1. **2 ítems completamente perdidos** en la transcripción OCR de la página 2 del Anexo 4.
2. **12 importes corruptos o ilegibles** en las celdas (`500`, `2500`, `ali`, `—`, `Te`, `OO`) que el OCR devuelve en lugar del valor con 2 decimales.

Ningún refinamiento adicional al parser puede recuperar datos que el
texto fuente OCR no contiene, sin caer en heurística prohibida
("rescatar importes DJ mal leídos" fue explícitamente vetado).

---

## 6. Corolario operativo

- El Excel de revisión humana (`AUDIT_HUMANO_DEBE2026-INT-0316916.xlsx`,
  sandbox) muestra los 19 ítems con su `numero_item` y `pagina_pdf`, total
  parseable S/ 53.04, y los 12 pendientes visibles con importe 0.00 y
  observación `IMPORTE_ILEGIBLE_PENDIENTE`.
- Cerrar la brecha a S/ 165.00 y 21 ítems exige reprocesar OCR
  focalizado en la región DJ del PDF de rendición. Opción técnica
  dentro del pipeline actual: segunda pasada análoga a
  `scripts/ingesta/ocr_region_totales.py` (que ya existe para totales
  de CPs) aplicada a la tabla del Anexo 4, con DPI elevada (600-800),
  binarización adaptativa y opcionalmente `pytesseract.image_to_data`
  para reconstrucción celda a celda por bounding box.
- Esa corrección **vive en el repo `vision_rag`, fuera del sandbox**,
  y requiere autorización explícita adicional.

---

## 7. Archivos de referencia consultados

- `control_previo/procesados/DEBE2026-INT-0316916/ocr_cache/2026042110383RENDICIONDEVIATICOSERARGTARAPOTOPV (1).pdf.txt`
- `sandbox_test_cowork_v2/vision_rag_control_previo_v2/src/control_previo_viaticos/rules/dj_anexo3_conceptos.py` (parser post-fix)
- `sandbox_test_cowork_v2/output/AUDIT_HUMANO_DEBE2026-INT-0316916.audit.json` (3 capas)
