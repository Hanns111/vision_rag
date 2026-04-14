# Ingesta de expedientes reales → Excel de validación humana

**Estado:** piloto operativo desde 2026-04-14 (primer caso real: `DIED2026-INT-0250235`).

Infraestructura para convertir carpetas sueltas de expedientes (como llegan) en
extractos clasificados que un humano puede revisar en Excel. Alimenta el
ground truth del PASO 0 y sirve de base para el PASO 7 formal.

No sustituye el pipeline de métricas formales (`data/piloto_ocr/metrics/METRICAS_MINIMAS.md`).

---

## 1. Lectura de texto: OCR por-página (text_reader v2)

Desde 2026-04-14, `scripts/ingesta/text_reader.py` decide **por página**
(no por documento) si aplica OCR:

- PyMuPDF extrae texto nativo de cada página.
- Si `len(texto_nativo.strip()) < 50` → Tesseract OCR sobre **esa sola página**.
- Un único motor por página → sin duplicación. El `.txt` lleva marcadores
  `===== PAGE N (motor=...) =====` que prueban el origen de cada bloque.
- Cache por sha1 del PDF. El `.meta.json` registra por página: motor,
  `len_texto`, status; y por documento: `paginas_nativas`, `paginas_ocr`.
- Fallback tolerante: OCR fallido de una página → `sin_texto_ocr_fallido`,
  pipeline continúa. Umbral configurable: `_MIN_CHARS_PAGE_NATIVE = 50`.

Impacto medido sobre `DIED2026-INT-0250235` (RENDIC 150 páginas):

| | Antes (v1) | Después (v2) |
|---|---|---|
| Páginas con texto | 102/150 | **143/150** |
| Caracteres totales | 75 134 | **130 651** (+74%) |
| Tiempo 1ª corrida | ~3 s | ~60 s (41 páginas OCR) |
| Tiempo con cache | ~1 s | ~1 s |

Resultado en `id_resolver` (más evidencia disponible): aparecen
`EXP-DIED-2026-250235` y un segundo SIAF legítimo (Expediente SIAF del
movimiento contable) que antes quedaban invisibles en las páginas escaneadas.

---

## 2. Flujo (cuatro etapas, cada una idempotente)

```
DIED2026-INT-0250235/                ← pegas carpeta/PDFs aquí (gitignored)
     │
     ▼   scan
control_previo/procesados/{id}/
├── source/                          ← copia de PDFs (no mueve originales)
├── ocr_cache/                       ← {archivo}.txt + .meta.json (cache por sha1)
├── extractions/                     ← {archivo}.json (tipo + campos + confianza)
├── metadata.json                    ← expediente_id, hashes, fecha_ingesta
└── _trace.log                       ← timestamps de cada acción
     │
     ▼   process (lee texto → clasifica → extrae)
extractions/{archivo}.json
     │
     ▼   export
data/piloto_ocr/metrics/validacion_expedientes.xlsx
```

Todas las etapas son **re-ejecutables sin riesgo**: cache por SHA-1 de archivo,
upsert por `(expediente_id, archivo)` en el Excel.

---

## 2. Uso

### Ingresar un expediente nuevo

```bash
# pegá la carpeta en la raíz del repo (ej: DIED2026-INT-0250235/)
python scripts/ingest_expedientes.py run-all --src DIED2026-INT-0250235
```

Genera `control_previo/procesados/DIED2026-INT-0250235/` completo y actualiza
`data/piloto_ocr/metrics/validacion_expedientes.xlsx`.

### Subcomandos individuales

```bash
python scripts/ingest_expedientes.py scan    --src DIED2026-INT-0250235
python scripts/ingest_expedientes.py process --expediente-id DIED2026-INT-0250235
python scripts/ingest_expedientes.py export                    # todos los expedientes
python scripts/ingest_expedientes.py export  --expediente-id DIED2026-INT-0250235
```

### Reprocesar ignorando cache

```bash
python scripts/ingest_expedientes.py process --expediente-id DIED2026-INT-0250235 --force
```

---

## 3. El Excel de validación

`data/piloto_ocr/metrics/validacion_expedientes.xlsx` tiene 3 hojas:

### Hoja `documentos` — una fila por archivo

Columnas del sistema (gris):

| Columna | Origen |
|---|---|
| `expediente_id` | nombre de la carpeta de ingesta |
| `archivo` | nombre del PDF |
| `ruta_origen` | ruta absoluta antes de la copia |
| `tipo_documento_detectado` | `classifier.py` |
| `confianza_tipo` | ∈ [0, 1] |
| `monto_detectado` | `extractor.py` (PASO 4.1) |
| `fecha_detectada` | idem |
| `ruc_detectado` | idem |
| `razon_social_detectada` | idem |
| `numero_documento_detectado` | serie-número |
| `tipo_gasto_detectado` | mapeo del tipo documental |
| `texto_extraido_resumen` | primeras ~400 chars |
| `estado_procesamiento` | `ok` / `bajo_confianza` / `error` |
| `nota_sistema` | overrides / errores trazables |

Columnas humanas (amarillo, se **preservan en cada re-export**):

`tipo_correcto · monto_correcto · fecha_correcta · ruc_correcto · observaciones · validacion_final`

### Hoja `expedientes` — resumen por `expediente_id`

Conteos: `n_documentos`, `n_ok`, `n_bajo_confianza`, `n_error`, `tipos_detectados`.

### Hoja `errores` — subset de documentos con `estado_procesamiento = error`

---

## 4. Cómo se clasifica (resumen)

9 categorías + `tipo_desconocido`:

`solicitud · oficio · anexo · factura · orden_servicio · orden_compra · pasaje · rendicion · otros`

- Reglas regex con tres ámbitos: **texto completo**, **encabezado** (primeras
  ~2000 chars, peso extra por señalar meta-tipo), **nombre** del archivo.
- Cada regla aporta puntaje; gana el top. Si top_score < 3 → `tipo_desconocido`.
- **Override consolidado:** si el nombre contiene `RENDIC` y el encabezado
  muestra señales de rendición, el tipo final es `rendicion` aunque las
  facturas anidadas (sustento) acumulen más puntaje. Los otros tipos quedan
  en `subtipos_detectados` y `nota_sistema`.

Fuente: `scripts/ingesta/classifier.py`.

---

## 5. Cómo se extraen campos (resumen)

Wrapper de `piloto_field_extract_paso4` (PASO 4.1, ya existente).

- **No reimplementa reglas.** Mapea los campos internos al esquema del Excel.
- Confianza por campo derivada del id de `regla` del extractor:
  - `0.85` cuando la regla es firme (ej. `factura_repr_impresa_factura`)
  - `0.6` para fallbacks globales (ej. `serie_FE_global_plain`)
  - `0.4` para skips por no aplicar
  - `0.0` cuando el valor es `None`
- `tipo_gasto` se infiere del `tipo_documento_detectado` (conservador).

Fuente: `scripts/ingesta/extractor.py`.

---

## 6. Principios no negociables

- **No inventa datos.** Si no hay señal, el campo queda `None` con confianza 0.
- **Idempotencia.** Cache por SHA-1; re-procesar no duplica ni reescribe
  trabajo humano en el Excel.
- **Trazabilidad.** Cada `extractions/{archivo}.json` incluye reglas de
  clasificación activadas, puntajes, `nota`, y traza completa del extractor
  PASO 4.1. `_trace.log` registra cada copia/OCR/clasificación con timestamp.
- **Originales intactos.** `scan` **copia**, no mueve. El original puede
  eliminarse de la raíz solo cuando Hans lo decida.

---

## 6-bis. Resolución de identidad + validaciones normativas

**Resolución de identidad administrativa** (`scripts/ingesta/id_resolver.py` +
`scripts/consolidador.py`): tras la extracción, detecta SINAD/SIAF/EXP/AÑO en
cada documento y los consolida en `expediente.json` (schema `expediente.v2`).
Detalle: `docs/RESOLUCION_EXPEDIENTE_ID.md`. Resultado en 9 columnas nuevas de
la hoja `documentos` y en la nueva hoja `resolucion_ids`.

**Firmas en Anexo 3** (`scripts/validaciones/firmas_anexo3.py`): solo si
`tipo_detectado == "rendicion"`. Detalle: `docs/VALIDACION_FIRMAS_ANEXO3.md`.
Resultado en columnas `validacion_firmas`, `estado_firmas`, `errores_firmas`,
`confianza_firmas`.

Ambas son desacopladas: si el módulo falla, el pipeline continúa.
Flags: `--skip-resolucion` y `--skip-validaciones`.

---

## 7. Limitaciones conocidas (primer piloto)

- PDFs **consolidados** (rendiciones con facturas/pasajes pegados adentro)
  reciben un solo tipo. El override marca el meta-tipo, pero los `subtipos`
  quedan solo como metadato. La extracción de montos/RUCs sobre texto completo
  confunde valores cruzados. → pendiente: extracción por rangos de páginas.
- El extractor PASO 4.1 está calibrado para documentos individuales, no para
  consolidados. Montos de rendición no se capturan todavía.
- OCR Tesseract a veces mezcla acentos en caracteres aislados (`�`). El texto
  base se preserva UTF-8 en la cache y el pipeline no corrompe datos.

Ver `CURRENT_STATE.md` para el contexto y `docs/ROADMAP_PROYECTO.md §0.3` para
el encaje con los PASO 0–7.

---

## 8. Archivos involucrados

```
scripts/
├── ingest_expedientes.py           CLI principal
└── ingesta/
    ├── __init__.py
    ├── scanner.py                  scan (hash + copia + metadata.json)
    ├── text_reader.py              PyMuPDF nativo + fallback OCR + cache
    ├── classifier.py               reglas regex + override consolidado
    ├── extractor.py                wrapper PASO 4.1
    └── excel_export.py             openpyxl, 3 hojas

control_previo/procesados/{id}/     salida (gitignored)
data/piloto_ocr/metrics/validacion_expedientes.xlsx   (versionado)
docs/INGESTA_EXPEDIENTES.md         este archivo
```
