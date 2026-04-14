# Resolución de identidad administrativa del expediente

**Módulos:** `scripts/ingesta/id_resolver.py` (detección) + `scripts/consolidador.py` (decisión)
**Modelo:** `scripts/modelo/expediente.py` (schema `expediente.v2`)
**Integración:** `scripts/ingest_expedientes.py` subcomandos `process` + `consolidate`
**Estado:** operativo desde 2026-04-14. Primer caso real: `DIED2026-INT-0250235`.

---

## 1. Objetivo

Determinar la identidad administrativa de un expediente (SINAD, SIAF, AÑO y
`expediente_id` canónico) con evidencia documental, **sin depender del nombre
de carpeta**. El nombre de carpeta se conserva como referencia (`expediente_id_carpeta`)
pero tiene peso bajo en el scoring.

---

## 2. Tipos de identificadores detectados

| Tipo | Patrón regex (simplificado) | Peso de tipo | Ejemplo |
|---|---|---|---|
| `sinad` | `SINAD\s*N?\s*[°.ºo]?\s*[:\-]?\s*(\d{4,8})` | **5** | `SINAD 250235` |
| `exp` | `([A-Z]{3,6})\s*(\d{4})-INT-(\d{6,8})` | **4** | `DIED2026-INT-0250235` |
| `oficio` | `OFICIO\s+N?\s*[°.ºo]?\s*(\d+-\d{4}-[A-Z/-]+)` | 3 | `OFICIO N° 123-2026-MINEDU/DIED` |
| `siaf` | `(?:N° Exp\s)?SIAF\s*[:\-]?\s*(\d{6,10})` | 2 | `SIAF: 2603426` |
| `anio` | desde fechas `dd/mm/YYYY`, `YYYY-MM-DD`, o del `exp` | 1 | `2026` |
| `planilla` | `N°\s*Planilla\s*[:\-]?\s*(\d{3,6})` | 1 | `00617` |
| `pedido` | `N°\s*Pedido\s*[:\-]?\s*(\d{3,6})` | 1 | `572` |

### Formato canónico

`TIPO-VALOR` con valor numérico sin ceros a la izquierda:

- `SINAD-250235`
- `SIAF-2603426`
- `EXP-DIED-2026-250235`
- `ANIO-2026`

---

## 3. Scoring determinista

```
score(id) = Σ_docs (peso_tipo_documento × peso_tipo_id × frecuencia_en_doc)
          + peso_nombre_carpeta × 1  (si el valor aparece en la carpeta)
```

| peso_tipo_documento | valor |
|---|---|
| rendicion | 4 |
| solicitud | 3 |
| oficio | 3 |
| anexo | 2 |
| factura / pasaje / orden_servicio / orden_compra / otros / tipo_desconocido | 1 |

`peso_nombre_carpeta = 1` (deliberadamente bajo — solo referencia).

---

## 4. Estados de resolución

Se calcula un estado por cada campo (`expediente`, `sinad`, `siaf`, `anio`):

| Estado | Condición |
|---|---|
| `OK` | `score_max ≥ 10` **y** `score_max / score_2do ≥ 2.0` |
| `CONFLICTO_EXPEDIENTE` | `score_2do / score_max ≥ 0.5` (dos candidatos fuertes) |
| `BAJA_CONFIANZA` | `score_max < 10` o dominancia < 2 |

El `estado_resolucion` global en `expediente.json` = el **peor** de los 4 estados
(orden: CONFLICTO > BAJA_CONFIANZA > OK). **Nunca se decide automáticamente** un
conflicto; el humano escoge en el Excel.

---

## 5. Integración en el pipeline

```
scan → process (classify, extract, 🆕 id_resolver, firmas_anexo3)
     → 🆕 consolidate (produce expediente.json)
     → export (→ Excel + hoja resolucion_ids)
```

- Desacoplado: si el módulo falla, el pipeline continúa (flag `--skip-resolucion`).
- Aditivo: ninguna salida existente cambia.
- Idempotente: el consolidador regenera `expediente.json` completo en cada corrida.

---

## 6. Archivos producidos

### `extractions/{archivo}.json` (nivel documento)

```json
"resolucion_id": {
  "candidatos_en_este_archivo": [
    {
      "id_canonico": "SINAD-250235",
      "tipo": "sinad",
      "valor_original": "250235",
      "frecuencia": 3,
      "fuentes": [
        {"pagina": 1, "fragmento": "...SINAD 250235...", "regla": "re_sinad_v1"}
      ]
    }
  ]
}
```

### `expediente.json` (nivel expediente — schema `expediente.v2`)

```json
{
  "schema_version": "expediente.v2",
  "expediente_id_carpeta": "DIED2026-INT-0250235",
  "resolucion_id": {
    "expediente_id_detectado": "SINAD-250235",
    "sinad": "250235",
    "siaf": "2603426",
    "anio": "2026",
    "confianza_expediente": 0.869,
    "confianza_sinad": 0.869,
    "confianza_siaf": 0.941,
    "confianza_anio": 0.957,
    "estado_resolucion": "OK",
    "coincide_con_carpeta": true,
    "candidatos": [ ... ordenados por score desc ... ],
    "observaciones": []
  }
}
```

---

## 7. Excel (`data/piloto_ocr/metrics/validacion_expedientes.xlsx`)

### Hoja `documentos` — 9 columnas nuevas (al final de las de sistema)

`expediente_detectado · sinad_detectado · siaf_detectado · anio_detectado · confianza_expediente · confianza_sinad · confianza_siaf · conflicto_expediente · observaciones_expediente`

Todas las filas del mismo expediente comparten valor (atributo de expediente, duplicado a propósito para permitir filtros por archivo).

### Hoja `resolucion_ids` — una fila por candidato

`expediente_carpeta · id_canonico · tipo · frecuencia · score_total · coincide_con_carpeta · es_ganador · estado_resolucion · fuentes`

Permite auditar por qué se eligió un ID frente a otros.

---

## 8. Resultado real sobre `DIED2026-INT-0250235`

### Candidatos detectados

| id_canonico | tipo | freq | score | ganador |
|---|---|---|---|---|
| `SINAD-250235` | sinad | 6 | **106** | **Sí** |
| `ANIO-2026` | anio | 6 | 22 | No |
| `SIAF-2603426` | siaf | 2 | 16 | No |
| `SINAD-112591` | sinad | 1 | 15 | No (cert. presupuestal — real, no ruido) |
| `PEDIDO-572` | pedido | 1 | 3 | No |

### Campos resueltos

| Campo | Valor | Confianza | Estado |
|---|---|---|---|
| `expediente_id_detectado` | `SINAD-250235` | 0.87 | OK |
| `sinad` | `250235` | 0.87 | OK |
| `siaf` | `2603426` | 0.94 | OK |
| `anio` | `2026` | 0.96 | OK |
| `estado_resolucion` (global) | — | — | **OK** |
| `coincide_con_carpeta` | sí | — | — |

**Interpretación**: el SINAD dominante (106) tiene dominancia 7× sobre el 2do SINAD (15), muy por encima del umbral de 2× → no hay conflicto. Un humano puede aun validar en el Excel y corregir si lo considera necesario.

---

## 9. Principios no negociables

1. **Nunca confiar solo en la carpeta.** Peso de carpeta = 1, deliberadamente bajo.
2. **No inventar.** Si no hay evidencia, campo `null` con `confianza = 0`.
3. **Trazabilidad completa.** Cada candidato lleva fragmento + regla + página + archivo.
4. **No forzar decisiones.** En `CONFLICTO_EXPEDIENTE`, el Excel expone ambos candidatos para revisión humana.
5. **Auditable.** Todos los scores y fuentes quedan en `expediente.json` y la hoja `resolucion_ids`.

---

## 10. Limitaciones conocidas

1. **OCR degradado** puede ocultar IDs (SINAD con un dígito perdido → distinto id_canonico). Mitigación pendiente: normalización por similitud (no implementada, introduce riesgo de invención).
2. **EXP (prefijo unidad)** solo se detecta si aparece dentro del texto de un documento. Hoy el caso piloto solo lo tiene en la carpeta, por eso no figura como candidato textual.
3. **Umbrales calibrados con 1 expediente**: `UMBRAL_MIN=10`, `DOMINANCIA_MIN=2.0`, `CONFLICTO_RATIO=0.5`. Recalibrar tras ≥5 expedientes reales.
4. **AÑO desde OCR**: puede venir de fechas de documentos sustento (facturas emitidas antes del expediente). Hoy se toma el más frecuente; si hay ambigüedad, documentar como observación.
