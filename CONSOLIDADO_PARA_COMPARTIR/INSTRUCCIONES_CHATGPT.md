# Cómo usar este paquete con ChatGPT

## Archivo principal para subir

**`SANTO_GRIAL_PARA_CHATGPT.zip`** (~30 MB comprimido en una corrida típica; el tuyo puede variar según el análisis).

Incluye:

| Contenido en el ZIP | Descripción |
|---------------------|-------------|
| **`00_LEE_PRIMERO_SANTO_GRIAL_TODO_EN_UNO.md`** | Misma síntesis que el “todo en uno”; empieza por aquí si el asistente solo abre un archivo. |
| **`INSTRUCCIONES_CHATGPT.md`** | Esta guía (copia dentro del zip). |
| **`SANTO_GRIAL_ANALYSIS/`** | Pipeline (`*.js`), `output/` reconstruido, `PROJECT_INDEX.json`, `SYSTEM_*`, `SYSTEM_BLUEPRINT/`, `CODIGO_FUENTE_RECONSTRUIDO/`, etc. |
| **`agent_sandbox_python_audit/`** | Copia del sandbox Python (`AGENT_SANDBOX_SOURCE_FOR_AUDIT`) para contrastar. |

## Pasos

1. En ChatGPT (cuenta con **subida de archivos**), adjunta **`SANTO_GRIAL_PARA_CHATGPT.zip`**.
2. Escribe algo como: *“Tienes el zip del proyecto Santo Grial: primero lee `00_LEE_PRIMERO_SANTO_GRIAL_TODO_EN_UNO.md`, luego profundiza en `SANTO_GRIAL_ANALYSIS/SYSTEM_BRAIN_CONFIRMED.md` y en lo que necesites bajo `output/src/`.”*
3. Si **no acepta el zip** por tamaño o política: sube solo **`SANTO_GRIAL_TODO_EN_UNO.md`** y pide análisis de arquitectura; para código pásale después archivos concretos del análisis.

## Regenerar el ZIP

En PowerShell, desde esta carpeta:

```powershell
.\empaquetar_para_chatgpt.ps1
```

Vuelve a generar **`SANTO_GRIAL_PARA_CHATGPT.zip`** tras cambiar el análisis o el `SANTO_GRIAL_TODO_EN_UNO.md`.

## Aviso

No ejecutes en tu máquina binarios o scripts del material empaquetado sin revisarlos. Uso previsto: **lectura y análisis** con un LM.
