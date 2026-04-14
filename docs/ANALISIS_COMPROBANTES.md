# Análisis de comprobantes dentro de rendiciones

**Módulos:**
- `scripts/ingesta/comprobante_detector.py` — segmentación en bloques
- `scripts/ingesta/comprobante_extractor.py` — wrapper PASO 4.1 por bloque + deduplicación
- `scripts/modelo/expediente.py` — `Comprobante` y `FlujoFinanciero` (schema `expediente.v3`)

**Integración:** `scripts/ingest_expedientes.py process` sobre archivos `tipo_detectado = "rendicion"`; consolidador agrega al `expediente.json`.

**Estado:** operativo desde 2026-04-14. Primer caso real: `DIED2026-INT-0250235`.

---

## 1. Objetivo

Hacer visibles los comprobantes (facturas, boletas, tickets) embebidos en
rendiciones consolidadas de viáticos, para que el validador humano pueda
auditar el sustento sin abrir el PDF de 150 páginas.

No sustituye revisión humana: el OCR degrada montos; el pipeline expone la
evidencia y marca inconsistencias trazables.

---

## 2. Flujo

```
texto concatenado (ocr_cache/{archivo}.txt con marcadores PAGE N)
   │
   ▼  comprobante_detector.detectar_bloques
BloqueComprobante[ ]
   │  señales: cabecera (FACTURA/BOLETA/TICKET + serie [EFB]\d{3}-\d+),
   │  cuerpo (RUC 11 dígitos + IGV/IMPORTE TOTAL)
   │  agrupamiento: ventana 1–3 páginas
   │
   ▼  comprobante_extractor.extraer_de_bloque (PASO 4.1 sobre el bloque)
Comprobante[ ]  (con ruc, serie, fecha, monto, razón social, confianza)
   │
   ▼  deduplicar por (ruc|serie|fecha|monto), fallback hash(texto[:1500])
Comprobantes únicos
   │
   ▼  consolidador agrega al expediente.json + FlujoFinanciero
```

---

## 3. Modelo (`schema expediente.v3`)

```python
@dataclass
class Comprobante:
    archivo: str
    pagina_inicio: int
    pagina_fin: int
    tipo: str                 # factura_electronica | boleta_venta | ticket | desconocido
    ruc: str | None
    razon_social: str | None
    serie_numero: str | None  # "E001-16"
    fecha: str | None         # YYYY-MM-DD
    monto_total: str | None
    moneda: str | None
    monto_igv: str | None
    confianza: float          # proporción de campos core llenos
    hash_deduplicacion: str
    texto_resumen: str        # primeros ~300 chars

@dataclass
class FlujoFinanciero:
    total_detectado: str      # suma de monto_total (solo comprobantes con monto)
    moneda: str               # moneda dominante
    n_comprobantes: int
    n_facturas: int
    n_boletas: int
    n_tickets: int
    n_desconocidos: int
    inconsistencias: list[str]  # sin_monto, monto_no_parseable (tope 50)
```

---

## 4. Excel — hoja `comprobantes`

Una fila por comprobante único, ordenada por expediente → archivo → página.

**Columnas de sistema (14):**
`expediente_id · archivo · pagina_inicio · pagina_fin · tipo · ruc · razon_social · serie_numero · fecha · monto_total · moneda · monto_igv · confianza · texto_resumen`

**Columnas humanas (amarillo, 5):**
`monto_correcto · ruc_correcto · proveedor_correcto · observaciones · validacion_final`

Se preservan entre re-exports por clave `(expediente_id, archivo, pagina_inicio, pagina_fin)`.

---

## 5. Resultado real sobre `DIED2026-INT-0250235`

| Métrica | Valor |
|---|---|
| Bloques detectados | 47 |
| Comprobantes únicos tras deduplicación | **34** |
| Facturas electrónicas | 21 |
| Boletas de venta | 13 |
| Tickets | 0 |
| Comprobantes con RUC | 26 / 34 (76%) |
| Comprobantes con fecha | 30 / 34 (88%) |
| Comprobantes con serie | 13 / 34 (38%) |
| Comprobantes con monto | **4 / 34 (12%)** |
| Total detectado | **S/ 428.64 PEN** |
| Monto recibido real (anexo 3) | S/ 4,980.00 |
| Cobertura automática del monto | ~9% |
| Inconsistencias trazables (`sin_monto`) | 30 |

### Proveedores reconocidos (texto legible tras OCR)

- CEBICHERIA COQUITO S.A.C. (RUC 20539971477)
- AR REPRESENTACIONES GASTRO… (RUC 20609385317)
- INVERSIONES & SERVICIOS MU… (RUC 20477689699)
- … y otros 20 con RUC pero sin razón social capturada

---

## 6. Limitaciones conocidas

1. **OCR degrada montos en facturas escaneadas**: "IGV: S/ 18.00" puede salir como "lGV S. 18 OO" y el regex de monto no matchea. Efecto: 88% de comprobantes sin monto. Mitigación futura: OCR por zonas (ROI) o LLM fallback (PASO 5 del roadmap).
2. **PASO 4.1 calibrado para facturas individuales**: fragmentos de consolidado pueden romper la lógica cabecera/cuerpo del extractor; razón social queda None cuando el logotipo de cabecera está en imagen no OCR.
3. **Fecha fuera de rango del viaje**: pueden aparecer fechas de emisión posteriores al viaje (ej. factura de hotel emitida días después). Hoy no se valida contra rango del comisionado; se documenta como tarea futura.
4. **Detección de "resumen Anexo 3"**: la página 1 del RENDIC trae un listado SIGA con series como `E001-16` — genera un bloque espurio. Filtro pendiente en `comprobante_detector`.
5. **Tickets sin RUC ni serie**: hoy permitimos RUC null pero se trata como `desconocido` con confianza baja. Adecuado para validación, no para agregación automática de montos.

---

## 7. Principios no negociables

- **No inventar**: si OCR no captura monto → `null` + confianza 0. No se estima.
- **Trazabilidad**: cada comprobante lleva `archivo` + `pagina_inicio` / `pagina_fin` + `texto_resumen`. El humano puede abrir el PDF en la página exacta.
- **Idempotencia**: `hash_deduplicacion` asegura que re-ejecutar no duplica filas en el Excel; columnas humanas se preservan.
- **Desacoplado**: solo corre si `tipo_detectado == "rendicion"`. Flag `--skip-comprobantes` desactiva el paso sin tocar código.

---

## 8. Uso

```bash
# Pipeline completo (incluye detección de comprobantes)
python scripts/ingest_expedientes.py run-all --src DIED2026-INT-0250235

# Solo proceso + consolidado (sin nuevo export)
python scripts/ingest_expedientes.py process     --expediente-id DIED2026-INT-0250235
python scripts/ingest_expedientes.py consolidate --expediente-id DIED2026-INT-0250235

# Omitir detección
python scripts/ingest_expedientes.py process --src DIED2026-INT-0250235 --skip-comprobantes
```

---

## 9. Archivos involucrados

```
scripts/
├── ingesta/
│   ├── comprobante_detector.py     🆕 segmentación por bloques
│   └── comprobante_extractor.py    🆕 wrapper PASO 4.1 + deduplicación
├── modelo/
│   └── expediente.py               ✏️ Comprobante + FlujoFinanciero
├── consolidador.py                  ✏️ agrega comprobantes al expediente.json
├── ingest_expedientes.py            ✏️ process corre detector + extractor
└── ingesta/excel_export.py         ✏️ hoja `comprobantes`

docs/ANALISIS_COMPROBANTES.md       🆕 este archivo
```
