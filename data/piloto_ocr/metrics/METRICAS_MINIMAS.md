# Métricas mínimas comparables (PASO 1–2)

Alineado a **`docs/ROADMAP_PROYECTO.md` §4.3** y **[`../PILOTO_OPERATIVO.md`](../PILOTO_OPERATIVO.md)** (mismas páginas que el manifiesto). Los CSV deben poder **unirse** por `(doc_id, page_index, campo)`.

## Columnas sugeridas por fila (CSV)

| Columna | Descripción |
|---------|-------------|
| `doc_id` | Igual que en labels |
| `page_index` | Igual que en labels |
| `campo` | Una de las claves de `campos` |
| `valor_gold` | Desde JSON etiquetado |
| `valor_pred` | Salida del motor OCR/parsing |
| `exactitud` | 0 o 1 según §4.3 roadmap |
| `motor` | `tesseract_baseline`, `paddleocr`, etc. |
| `fecha_corrida` | ISO date |

## Archivos

- `baseline_paso1_YYYYMMDD.csv` — solo PASO 1.
- `bakeoff_paso2_<motor>_YYYYMMDD.csv` — PASO 2; un archivo por motor o una hoja con columna `motor`.

## Tiempo

Registrar en el mismo CSV o en `run_log_YYYYMMDD.txt`: tiempo total de corrida y **segundos_por_pagina** = tiempo / 15.

## Entorno de ejecución (criterio preferente — PASO 1–2)

Los resultados numéricos son **comparables solo entre motores corridos en el mismo entorno** (misma máquina, mismo OS, mismas versiones). Las métricas de PASO 2 deben interpretarse **siempre según el entorno documentado** (OS, CPU/GPU, versiones, notas de fallo).

**Criterio preferente del proyecto:** para **OCR avanzado** y **bake-off PASO 2**, el entorno **preferente** es **Linux/Ubuntu vía WSL** cuando permita mayor estabilidad y uso adecuado de **GPU**; **Windows** queda como **secundario** cuando existan limitaciones de runtime que distorsionen la comparación. Un fallo solo en Windows **no** implica descarte definitivo del motor si en **Linux/WSL** la herramienta es reproducible.

Ver **[`../PILOTO_OPERATIVO.md`](../PILOTO_OPERATIVO.md) §7** y **`docs/DECISIONES_TECNICAS.md` D-12**.
