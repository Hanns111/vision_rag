# Changelog

Todos los cambios notables del proyecto se documentan aquí.

---

## [2026-04-08]

### RAG — Chunking v4 y diagnóstico estructural

- **Índice:** `INDEX_SCHEMA_VERSION = 4`; reconstrucción obligatoria al subir de versión.
- **Chunking:** cortes por encabezados normativos; soporte **parcial** para numeración en una línea + título en la siguiente (`sec_linea_num_pendiente`); reglas para no fusionar líneas erróneas (TOC `1.`, números sin estructura de sección).
- **Anexos:** omisión de corte tipo anexo solo en filas de **índice** (TOC / puntos guía), para limitar micro-chunks; cuerpo conserva cortes fuertes donde aplica.
- **Títulos:** limpieza ampliada (basura, entradas tipo índice/anexo); umbral de líneas en mayúsculas ajustado (`len >= 20`) con exclusiones.
- **Cross-encoder:** `max_length=1024` (sin cambio de modelo BGE).
- **Multi-view retrieval:** pool 10 (6 + 2 + 2) sin subir K global de salida.

### Resultados

- **Benchmark (entorno típico pairwise / sin GPU):** regresión a **12/18** respecto a corridas anteriores (~16/18).
- **Causa principal documentada:** desalineación entre **chunking** y estructura real del PDF (índice vs cuerpo, secciones 6.x, anexos, títulos), no atribuible solo a embeddings o CE.

### Documentación

- Añadido `docs/CURRENT_STATE_RAG.md` con arquitectura, diagnóstico y **NEXT STEP**.
