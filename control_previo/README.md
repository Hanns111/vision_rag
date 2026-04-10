# control_previo — Normativa por categoría + expedientes a revisar

**Propósito:** cada **categoría** de trámite MINEDU tiene **su propia normativa** (`normativa/`) y **sus expedientes** que entregas para revisión (`expedientes_revision/`). No es un único corpus mezclado: al indexar o auditar, usar **metadatos** `categoria` + `id_expediente`.

**Sustituye a la carpeta antigua** `NORMATIVAS CONTROL PREVIO_ 06.02.2026` (contenido migrado aquí el 2026-04-09).

---

## Estructura

| Carpeta | Contenido |
|---------|-----------|
| `01_viaticos/` | Directivas y anexos de viáticos (vigente feb. 2026 + histórico); plantillas; **expedientes viáticos** (p. ej. DIPLAN). |
| `02_os_oc_pautas/` | PAUTAS remisión expedientes de pago + contratos menores UE. |
| `03_caja_chica/` | RJ 042-2026, directiva 2026, clasificadores MEF, RJ 2025 obsoleta posible. |
| `04_encargos/` | Directiva de encargos (261-2018, etc.). |
| `05_detracciones/` | Normas SUNAT, expedientes ejemplo OGEPER, CIIU construcción. |
| `06_subvenciones/` | **Normativa FONDEP / RM:** preparar aquí o solo en cada expediente; **expedientes** (p. ej. FGE UGEL Huancayo). |
| `07_referencia_institucional/` | Concurso integridad, material no propio de “pago expediente” salvo contexto. |

En cada `NN_*` hay:

- **`normativa/`** — instructivos y referencias legales/técnicas.
- **`expedientes_revision/`** — una **subcarpeta por expediente** (tú copias aquí lo que hay que revisar).

---

## Viáticos — qué es vigente

| Uso | Ubicación |
|-----|-----------|
| **Trámites nuevos (2026)** | `01_viaticos/normativa/DIRECTIVAS DE VIÁTICOS_.../NUEVA_DIRECTIVA DE VIÁTICOS_F.DE APROB_ 05.02.2026/` (directiva DI-003-01 V03, RSG 023-2026, oficios). |
| **Solo expedientes antiguos** | `.../ANTIGUA_DIRECT_VIATICOS_HASTA_05_02_2026/` (directiva 011-2020). |
| **Plantillas de armado** | `01_viaticos/normativa/VIÁTICOS_PLANTILLA_2026/` |

---

## Expedientes ya ubicados

| Expediente | Ruta |
|------------|------|
| Viáticos DIPLAN 2026 | `01_viaticos/expedientes_revision/VIÁTICO_DIPLAN2026-INT-0283297/` |
| Viáticos DEBEDSAR 2026 | `01_viaticos/expedientes_revision/DEBEDSAR2026-INT-0103251/` *(reubicado desde la raíz del repo el 2026-04-09)* |
| Subvenciones FGE UGEL Huancayo | `06_subvenciones/expedientes_revision/SUBVENCIONES_FGE2025-INT-1081440_UGEL HUANCAYO/` |

---

## Corpus RAG / proyecto

- **Normativa por categoría:** alimentar índices con rutas bajo `normativa/` y etiqueta `tipo=viaticos|os_oc|…`.
- **Evidencia de caso:** solo bajo `expedientes_revision/<carpeta_expediente>/`.
- Ver `docs/ROADMAP_PROYECTO.md` y `docs/CONTROL_PREVIO_TAXONOMIA_EXPEDIENTES.md`.

---

## Manifiestos de ingestión

Cada `NN_*` incluye **`MANIFEST_INGESTION.csv`** (lista de archivos con `prioridad_ingest`, `rol`, `notas`). El agregado está en **`MANIFEST_INGESTION_TODO.csv`**.

Regenerar tras añadir o mover PDF:

`python scripts/gen_control_previo_manifests.py`

Nuevos archivos sin clasificar: colócalos directamente en **`normativa/`** o **`expedientes_revision/<carpeta>/`** de la categoría que toque.
