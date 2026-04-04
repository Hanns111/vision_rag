# Reporte final — SANTO_GRIAL_ANALYSIS

Este directorio debe contener:

| Elemento | Descripción |
|---------|-------------|
| `proyecto.map` | Source map de entrada |
| `extract.js` | Extracción a `./output/` |
| `index-project.js` | Índice + JSON + grafos |
| `detect-brain.js` | `SYSTEM_BRAIN.md` |
| `consolidate.js` | Núcleo en `CODIGO_FUENTE_RECONSTRUIDO/` |
| `verify.js` | Checklist |
| `run-pipeline.js` | Todo en secuencia |

## Ejecución

```bash
node run-pipeline.js
```

O paso a paso:

```bash
node extract.js
node index-project.js
node detect-brain.js
node consolidate.js
node verify.js
```

Después de ejecutar, revise la salida de `verify.js` y los totales impresos.

## Consolidación

La carpeta `CODIGO_FUENTE_RECONSTRUIDO/` incluye solo archivos **no vacíos** bajo el código propio del mapa (**se excluye `node_modules/`** para no mezclar vendor con núcleo). Se priorizan categorías `agents`, `tools`, `policy`, `prompts`, alto `weight_score`, el candidato SYSTEM_BRAIN y dependencias internas resueltas (tope ~90 archivos). Detalle por archivo: `_MANIFEST.json` en esa carpeta.

## Última ejecución verificada (referencia)

- Archivos en `./output`: **4756** (todos los extraídos del map).
- Archivos `.js` / `.ts` / `.tsx` indexados en `output`: **4532**.
- Archivos copiados a `CODIGO_FUENTE_RECONSTRUIDO` (sin `_MANIFEST.json`): **90**.
- SYSTEM_BRAIN (candidato por score): **`src/main.tsx`** — validación estricta en esta corrida: **hipótesis** (ver `SYSTEM_BRAIN.md`).
