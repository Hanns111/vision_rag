# Control previo — Taxonomía de expedientes e instructivos

> Modelo para organizar **expedientes de pago** en `vision_rag`: cada **categoría** tiene uno o más **instructivos** (norma, directiva, oficio, RJ). Las **subcategorías** existen cuando el trámite es **variable** (p. ej. subvenciones: el órgano que administra el fondo define el paquete documental).

**No confundir** con **`PASO 0–7`** del roadmap técnico (`docs/ROADMAP_PROYECTO.md` §0): allí se explica que `control_previo/01_viaticos` etc. son **categorías de negocio**, no pasos del pipeline OCR/RAG.

**Actualizado:** 2026-04-09

---

## 1. Modelo de datos (conceptual)

```
tipo_expediente          # ej. viáticos, encargo, subvención, planilla, caja_chica, os_oc…
  └── subcategoria?      # obligatoria si el tipo es heterogéneo (ej. subvención → FONDEP | otro)
       └── instructivo(s)  # PDF o conjunto normativo que manda el checklist
            └── version / vigencia
```

| Campo | Uso |
|-------|-----|
| `tipo_expediente` | Clasificación de **negocio** para revisión y routing de reglas. |
| `subcategoria` | Solo si aplica (subvenciones casi siempre; OS/OC puede depender de objeto). |
| `instructivo` | Fuente normativa **prioritaria** para el checklist (no sustituye ley/reglamento superior). |
| `pautas_marco` | Documento transversal que lista **categorías** y **remisión** (p. ej. pautas OS/OC). |

---

## 2. Categorías previstas (MINEDU — control previo)

Incluye lo que comentaste y huecos explícitos.

| ID | Categoría | Subcategoría típica | Notas |
|----|-----------|---------------------|--------|
| `os_oc` | Órdenes de servicio / órdenes de compra (objeto contractual) | Por objeto / modalidad si aplica | Suele apoyarse en **PAUTAS remisión expedientes pago**. |
| `viaticos` | Viáticos | Nacional / otros según directiva | Directiva + oficios de aprobación vigentes. |
| `encargos` | Encargos | — | Directiva de encargos (histórico 261-2018, etc.). |
| `subvenciones` | Subvenciones | **FONDEP**, otros fondos / unidades | **Atípico:** el paquete documental depende del **órgano** y de la RM vigente. Ejemplo repo: FONDEP + RM 507/484/… |
| `planillas` | Planillas (pagos masivos / remuneraciones) | Tipo de planilla si aplica | Categoría separada de “OS/OC” cuando el flujo es planilla. |
| `caja_chica` | Caja chica | — | RJ + directiva sectorial (ej. 2026). |
| `dietas` | Dietas | — | **Confirmar** en pautas OS/OC o norma específica. |
| `propinas` | Pago de propinas | — | **Confirmar** si figura como tipo propio o bajo “otros”. |
| `otros` | Otros objetos de gasto | — | Catch-all hasta cerrar taxonomía con tus PDF de pautas. |

**Regla:** todo lo que aparezca en el PDF de **PAUTAS PARA LA REMISIÓN…** debe convertirse en fila de esta tabla (o en `otros` con etiqueta hasta desglosar).

---

## 3. Instructivos que ya referenciaste (rutas OneDrive — no en el repo)

Copiar al árbol local recomendado (§4) cuando sincronices; aquí solo **mapeo lógico**.

| Archivo (nombre corto) | Encaje en taxonomía |
|--------------------------|---------------------|
| `PAUTAS PARA LA REMISIÓN DE EXPEDIENTES DE PAGO REVISION CONTROL PREVIO 11 07 07 2020.pdf` | **`pautas_marco`** — define/remite categorías y criterios de remisión; **índice maestro** para completar la tabla §2. |
| `RESOLUCION_JEFATURAL-00042-2026-MINEDU-SG-OGA.pdf` | **Caja chica** — RJ. |
| `2026031716498directivadecajqchica2026ULTIMOpd.pdf` | **Caja chica** — directiva 2026. |
| `OFICIO_MULTIPLE-00016-2026-MINEDU-SG-OGA_condición Activo y Habido.pdf` | **Viáticos** — oficio múltiple (condición aprobación). |
| `01_DIRECTIVA_DI-003-01-MINEDU_V03_05.02.2026_Viaticos_nacionales.pdf` | **Viáticos** — directiva nacional. |
| `Directiva de Encargos 261-2018.pdf` | **Encargos**. |

**Subvenciones / FONDEP:** el expediente ya trabajado en el repo (`SUBVENCIONES_FGE2025-INT-1081440_UGEL HUANCAYO`) es ejemplo de **`subvenciones` → `FONDEP`** + corpus RM/norma técnica en `00_normativa_base/`.

---

## 4. Estructura en el repo (implementada)

**Carpeta viva:** [`control_previo/README.md`](../control_previo/README.md)

Cada categoría tiene **`normativa/`** + **`expedientes_revision/`** (subcarpeta por expediente). Ejemplo:

```
control_previo/
  01_viaticos/
    normativa/          # directivas, plantillas, antigua vs nueva
    expedientes_revision/
      VIATICO_DIPLAN2026-INT-0283297/   # ejemplo
  02_os_oc_pautas/
    normativa/
    expedientes_revision/
  03_caja_chica/
  04_encargos/
  05_detracciones/
  06_subvenciones/
    normativa/          # (opcional) RM FONDEP global; o solo dentro de cada expediente
    expedientes_revision/
      SUBVENCIONES_FGE2025-INT-1081440_UGEL HUANCAYO/
  07_referencia_institucional/
```

La antigua carpeta `NORMATIVAS CONTROL PREVIO_ 06.02.2026` fue **migrada** aquí; ver `docs/MIGRACION_NORMATIVAS_2026-02-06.md`. Manifiestos: `control_previo/*/MANIFEST_INGESTION.csv` y `scripts/gen_control_previo_manifests.py`.

---

## 5. Corpus normativo en `vision_rag` (siguiente uso)

| Necesidad | Dónde |
|-----------|--------|
| Preguntas **por tipo** de expediente | Índice RAG **por carpeta** o metadato `tipo_expediente` + `subcategoria`. |
| Pautas marco | `00_pautas_marco` como capa **transversal** (no mezclar con un solo corpus sin etiquetas). |
| Caso real (evidencia) | Carpetas tipo `SUBVENCIONES_*` / futuras `VIATICOS_*` — ver `docs/EXPEDIENTE_FGE2025-INT-1081440_ORGANIZACION.md`. |

No implementar ingest masivo hasta **PASO 0** cerrado (`docs/ROADMAP_PROYECTO.md` §4.1–§9); el piloto factura usa **N=15** y `piloto_ocr.v1` en `data/piloto_ocr/`; categorías MINEDU (`control_previo/`) son aparte.

---

## 6. Pendientes explícitos

- [ ] Extraer del PDF **PAUTAS remisión** la lista cerrada de **categorías** (incl. propinas, dietas, planillas) y actualizar §2.
- [ ] Decidir si **dietas / propinas** son tipos propios o van bajo `os_oc` / `otros`.
- [ ] Copiar PDF desde OneDrive al árbol §4 y enlazar rutas relativas en este archivo.
- [ ] Por **subvención**, mantener siempre `subcategoria = órgano` (FONDEP, …) en metadatos de expediente.

---

## 7. Referencias en el repo

| Documento | Contenido |
|-----------|-----------|
| `control_previo/README.md` | Árbol por categoría (`normativa/` + `expedientes_revision/`). |
| `docs/MIGRACION_NORMATIVAS_2026-02-06.md` | Cierre de carpeta antigua `NORMATIVAS CONTROL PREVIO_ 06.02.2026`. |
| `docs/ROADMAP_PROYECTO.md` | Orden OCR/RAG/medición. |
| `docs/EXPEDIENTE_FGE2025-INT-1081440_ORGANIZACION.md` | Puntero expediente subvención FONDEP. |
| `control_previo/06_subvenciones/expedientes_revision/SUBVENCIONES_.../05_indices_manifiestos/ORGANIZACION_EXPEDIENTE.md` | Ejemplo expediente + normas en `00_normativa_base`. |
