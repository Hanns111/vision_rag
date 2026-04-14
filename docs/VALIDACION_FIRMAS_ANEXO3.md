# Validación de firmas en Anexo 3 (rendición de viáticos MINEDU / SIGA)

**Módulo:** `scripts/validaciones/firmas_anexo3.py`
**Integración:** ejecutado desde `scripts/ingest_expedientes.py` (subcomando `process`)
sobre archivos con `tipo_detectado = "rendicion"`, **después de la extracción y
antes del export a Excel**.
**Estado:** operativo desde 2026-04-14. Primer caso real: `DIED2026-INT-0250235`.

---

## 1. Propósito

Verificar, bajo principios de **control interno / segregación de funciones**, la
coherencia de firmas en el Anexo 3 de rendición de viáticos. El módulo no
reemplaza la revisión humana; produce evidencia auditable que el validador
puede aceptar, corregir o rechazar en el Excel.

Roles validados:

| Rol | Etiquetas típicas en SIGA |
|---|---|
| `comisionado` | "FIRMA COMISIONADO", "COMISIONADO", "Sr(a): NOMBRE" |
| `jefe_unidad` | "V° B° DE JEFE DE ÓRGANO O UNIDAD", "JEFE DE UNIDAD" |
| `vb_coordinador` | "V° B° COORDINADOR ADMINISTRATIVO", "RESPONSABLE ADMINISTRATIVO" |

---

## 2. Principios no negociables

1. **No inventar firmas.** Un nombre solo se declara cuando hay un **anchor
   obligatorio** en la ventana del rol:
   - DNI adyacente (≤60 chars entre nombre y DNI)
   - "Sr(a): NOMBRE" (anchor SIGA estándar)
   - "Firmado digitalmente por: NOMBRE ... FAU" (firma digital)
   Sin anchor → `nombre = None` aunque la etiqueta del rol esté presente.
2. **Segregación de funciones:** comisionado ≠ jefe_unidad ≠ vb_coordinador
   (coincidencia difusa por intersección de apellidos/nombres ≥4 letras).
3. **Control jerárquico:** si el comisionado coincide con el bloque del jefe
   → `OBSERVADO` con código `comisionado_y_jefe_coinciden_requiere_superior`.
   Nota: sin base jerárquica externa no podemos validar que el superior
   haya firmado en lugar del propio comisionado.
4. **Desacoplado**: la función `validar(texto) → ValidacionFirmasResult`
   recibe solo texto. No conoce OCR ni Excel. El pipeline principal continúa
   aun si el módulo falla (validaciones = `null` en el JSON).

---

## 3. Estados posibles

| Estado | Cuándo |
|---|---|
| `CONFORME` | 3 roles detectados con nombre y sin violar segregación de funciones |
| `OBSERVADO` | al menos un rol ilegible, o violación de segregación |
| `INSUFICIENTE_EVIDENCIA` | comisionado sin nombre legible, o ninguna etiqueta de rol encontrada |

---

## 4. Códigos de error (`errores_firmas` en el Excel)

| Código | Significado |
|---|---|
| `sin_bloque_firmas_anexo3` | no se halló ninguna etiqueta de rol en el texto |
| `rol_no_detectado:{rol}` | etiqueta del rol ausente |
| `nombre_ilegible:{rol}:anchor={tipo}` | etiqueta presente pero sin anchor válido cercano |
| `segregacion_funciones:comisionado_y_jefe_coinciden_requiere_superior` | mismo nombre en dos roles incompatibles |
| `segregacion_funciones:comisionado_y_vb_coinciden` | ídem |
| `segregacion_funciones:jefe_y_vb_coinciden` | ídem |
| `texto_vacio` | input sin texto (corrupción o error upstream) |
| `excepcion:{msg}` | falla interna del validador (el pipeline no se rompe) |

---

## 5. Limitaciones conocidas

Este módulo trabaja **solo sobre texto**. No detecta:

- **Firmas manuscritas como trazo** sobre la hoja escaneada. Si el OCR no
  devuelve DNI o nombre cerca de la etiqueta, el rol queda marcado como
  `nombre_ilegible` aunque visualmente haya firma.
- **Sellos institucionales** (requieren CV).
- **Relación jerárquica real** entre personas. La regla "el comisionado
  siendo jefe firma su superior" se aproxima por coincidencia de nombre.

Estas limitaciones son **conscientes**. El paso natural (futuro) para
cerrar la brecha es un detector visual de firma (ROI + CV/YOLO) que
confirme la **presencia del trazo** independientemente del OCR. Ver
`docs/ROADMAP_PROYECTO.md §11.1` sobre OCR dirigido por regiones.

---

## 6. Resultado sobre el primer expediente real (`DIED2026-INT-0250235`)

| Archivo | Tipo detectado | validacion_firmas | estado_firmas | errores | confianza_firmas |
|---|---|---|---|---|---|
| `PV617…JULCAN.pdf` | solicitud | *(no aplica)* | — | — | — |
| `RENDIC…SINAD250235.pdf` | rendicion | `firmas_anexo3` | **INSUFICIENTE_EVIDENCIA** | `nombre_ilegible:comisionado:anchor=dni_sin_nombre_adyacente`; `nombre_ilegible:jefe_unidad:anchor=sin_anchor`; `rol_no_detectado:vb_coordinador` | 0.1 |

**Interpretación honesta:** el Anexo 3 del RENDIC **tiene firmas visibles
en el PDF físico**, pero el OCR Tesseract no captura nombres+DNI adyacentes
a las etiquetas `V° B° DE JEFE DE ÓRGANO` y `FIRMA COMISIONADO` (el trazo
manuscrito no es texto). El resultado `INSUFICIENTE_EVIDENCIA` **no afirma
que falten firmas**; afirma que el sistema no puede validarlas desde texto.
El validador humano debe revisar el PDF original y marcar
`validacion_final` en el Excel.

---

## 7. Traza y auditabilidad

Cada ejecución deja trazabilidad en tres capas:

1. **JSON por documento:** `control_previo/procesados/{id}/extractions/{archivo}.json`
   bloque `validaciones.firmas_anexo3` con `firmantes[].evidencia` (fragmento
   del texto alrededor de cada etiqueta encontrada).
2. **Excel:** columnas `validacion_firmas`, `estado_firmas`, `errores_firmas`,
   `confianza_firmas` (+ columnas humanas para corregir).
3. **Log de ingesta:** `control_previo/procesados/{id}/_trace.log`.

---

## 8. Ejemplo de uso

```bash
# Pipeline completo (ingesta + clasificación + extracción + firmas + Excel)
python scripts/ingest_expedientes.py run-all --src DIED2026-INT-0250235

# Omitir validaciones normativas (si se quiere correr solo el pipeline base)
python scripts/ingest_expedientes.py process --expediente-id DIED2026-INT-0250235 --skip-validaciones
```

---

## 9. Dónde vive cada pieza

```
scripts/validaciones/
├── __init__.py
└── firmas_anexo3.py             módulo determinista

scripts/ingest_expedientes.py    integración opcional en `process`
scripts/ingesta/excel_export.py  4 columnas en hoja "documentos"
docs/VALIDACION_FIRMAS_ANEXO3.md este archivo
```
