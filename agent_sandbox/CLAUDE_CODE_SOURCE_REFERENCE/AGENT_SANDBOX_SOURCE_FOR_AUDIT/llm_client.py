"""
Cliente LLM (OpenRouter) con validación, coherencia input↔tool, umbral de
confianza y fallback auditable a reglas.

Salida unificada de analizar_con_llm:
  intencion, tool, confianza, fuente

Variables de entorno:
  OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_HTTP_REFERER, OPENROUTER_TITLE
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

TOOLS_PERMITIDAS = frozenset(
    {"validar_ruc", "leer_pdf", "calcular_monto", "buscar_en_pdf"}
)

NORMATIVA_MARKERS = (
    "norma",
    "normas",
    "directiva",
    "directivas",
    "artículo",
    "articulo",
    "artículos",
    "articulos",
    "viático",
    "viatico",
    "viáticos",
    "viaticos",
)


def tiene_intencion_normativa(texto: str) -> bool:
    """Señales léxicas de consulta normativa / documental (sin IO)."""
    t = (texto or "").lower()
    return any(m in t for m in NORMATIVA_MARKERS)


TOOLS_GUIA = """
Herramientas permitidas (campo "tool" solo puede ser uno de estos identificadores o null):

1) validar_ruc
   Cuándo: el usuario quiere validar/consultar un RUC, número de contribuyente, tax id peruano, u números de documento tributario.
   Señales: palabra "ruc", "contribuyente", listados de 11 dígitos, etc.

2) buscar_en_pdf
   Cuándo: consultar normas, directivas, artículos, viáticos u otras disposiciones en la carpeta **corpus** (varios PDF); recuperación **semántica** local (embeddings + coseno).
   Señales: "norma", "directiva", "artículo", "viático(s)", referencias legales o reglamentarias.
   Preferir esta herramienta frente a leer_pdf cuando la intención es localizar información concreta en esos documentos.

3) leer_pdf
   Cuándo: leer, extraer texto general, resumir o analizar un archivo PDF sin foco normativo explícito.
   Señales: "pdf", extensión .pdf, "documento" en contexto de archivo.

4) calcular_monto
   Cuándo: sumar, totalizar, calcular dinero, montos, presupuesto, "cuánto cuesta".
   Señales: "monto", cantidades numéricas monetarias, "suma", "total".

No inventes nombres de herramientas. Si ninguna aplica: "tool": null.
Sé conservador: si hay duda, null y confianza baja.
"""

CONFIDENCE_THRESHOLD = 0.5
COHERENCE_PENALTY = 0.35

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def analizar_por_reglas(input_usuario: str) -> dict[str, Any]:
    """
    Clasificación determinista (respaldo). Confianza alta solo con señal clara.
    """
    t = (input_usuario or "").lower().strip()
    if "ruc" in t:
        return {"intencion": "consulta_ruc", "tool": "validar_ruc", "confianza": 0.92}
    if tiene_intencion_normativa(t):
        return {
            "intencion": "consulta_normativa_documento",
            "tool": "buscar_en_pdf",
            "confianza": 0.9,
        }
    if "pdf" in t or ".pdf" in t:
        return {"intencion": "lectura_pdf", "tool": "leer_pdf", "confianza": 0.92}
    if "monto" in t:
        return {"intencion": "calculo_monto", "tool": "calcular_monto", "confianza": 0.9}
    if re.search(r"\d{8,}", t) and any(
        x in t for x in ("documento", "número", "numero", "identificación", "identificacion")
    ):
        return {"intencion": "consulta_ruc", "tool": "validar_ruc", "confianza": 0.55}
    if re.search(r"\d", t) and any(
        x in t for x in ("suma", "total", "calcular", "cuánto", "cuanto", "precio")
    ):
        return {"intencion": "calculo_monto", "tool": "calcular_monto", "confianza": 0.55}
    return {"intencion": "desconocida", "tool": None, "confianza": 0.2}


def _prompt_clasificacion(consulta: str) -> str:
    return f"""{TOOLS_GUIA}

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin texto antes ni después) usar exactamente estas claves:
{{
  "intencion": "<string, breve, español>",
  "tool": <"validar_ruc" | "leer_pdf" | "calcular_monto" | "buscar_en_pdf" | null>,
  "confianza": <número entre 0.0 y 1.0, tu certeza en la elección>
}}

Reglas:
- "confianza" debe reflejar evidencia en el mensaje del usuario (no inventes certeza).
- Si no hay herramienta adecuada: "tool": null y confianza baja (p. ej. 0.2-0.4).

Consulta del usuario (texto exacto):
{consulta}
"""


def _parse_confianza(raw: Any) -> float:
    if raw is None:
        return 0.55
    try:
        c = float(raw)
    except (TypeError, ValueError):
        return 0.45
    return max(0.0, min(1.0, c))


def _extraer_json_desde_texto(raw: str) -> dict[str, Any] | None:
    texto = (raw or "").strip()
    if not texto:
        return None
    bloque = re.search(r"\{[\s\S]*\}", texto)
    if bloque:
        texto = bloque.group(0)
    try:
        data = json.loads(texto)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _normalizar_tool(tool: Any) -> tuple[str | None, bool]:
    """
    Devuelve (tool_normalizado, hubo_nombre_inventado).
    Inventado = string no null y no en TOOLS_PERMITIDAS.
    """
    if tool in (None, "", "null", "ninguna", "none", "NINGUNA"):
        return None, False
    if not isinstance(tool, str):
        return None, True
    s = tool.strip()
    if s in TOOLS_PERMITIDAS:
        return s, False
    return None, True


def _penalizar_coherencia(texto_usuario: str, tool: str | None, confianza: float) -> float:
    """Anti-alucinación básica: señales mínimas en el texto si se eligió tool."""
    if tool is None:
        return confianza

    low = (texto_usuario or "").lower()
    penalizado = confianza

    if tool == "leer_pdf":
        if "pdf" not in low and ".pdf" not in low:
            penalizado = min(penalizado, COHERENCE_PENALTY)

    elif tool == "buscar_en_pdf":
        tiene_norma = tiene_intencion_normativa(low)
        tiene_pdf = "pdf" in low or ".pdf" in low
        if not (tiene_norma or tiene_pdf):
            penalizado = min(penalizado, COHERENCE_PENALTY)

    elif tool == "validar_ruc":
        tiene_ruc = "ruc" in low or "contribuyente" in low
        tiene_digitos_largos = bool(re.search(r"\d{8,}", low))
        if not (tiene_ruc or tiene_digitos_largos):
            penalizado = min(penalizado, COHERENCE_PENALTY)

    elif tool == "calcular_monto":
        tiene_monto_palabra = "monto" in low or "total" in low or "suma" in low
        tiene_numero = bool(re.search(r"\d", low))
        if not (tiene_monto_palabra or tiene_numero):
            penalizado = min(penalizado, COHERENCE_PENALTY)

    return max(0.0, min(1.0, penalizado))


def _procesar_respuesta_llm(
    data: dict[str, Any], texto_usuario: str
) -> dict[str, Any] | None:
    intencion = data.get("intencion")
    if intencion is not None and not isinstance(intencion, str):
        intencion = str(intencion)
    if not (intencion and str(intencion).strip()):
        intencion = "desconocida"
    else:
        intencion = str(intencion).strip()

    confianza = _parse_confianza(data.get("confianza"))
    tool_raw = data.get("tool")
    tool, inventado = _normalizar_tool(tool_raw)

    if inventado:
        confianza = min(confianza, 0.35)

    confianza = _penalizar_coherencia(texto_usuario, tool, confianza)

    return {
        "intencion": intencion,
        "tool": tool,
        "confianza": confianza,
    }


def _empaquetar_reglas(fuente: str, reg: dict[str, Any]) -> dict[str, Any]:
    return {
        "intencion": reg["intencion"],
        "tool": reg["tool"],
        "confianza": reg["confianza"],
        "fuente": fuente,
    }


def _llamada_openrouter(consulta: str) -> str | None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()
    user_content = _prompt_clasificacion(consulta)

    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un clasificador de intenciones para un agente con herramientas "
                    "fijas. Solo respondes un único objeto JSON válido, sin comentarios ni markdown."
                ),
            },
            {"role": "user", "content": user_content},
        ],
        "temperature": 0,
        "max_tokens": 320,
    }

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.environ.get(
                "OPENROUTER_HTTP_REFERER", "https://localhost"
            ),
            "X-Title": os.environ.get("OPENROUTER_TITLE", "agent_sandbox"),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        content = payload["choices"][0]["message"]["content"]
        return content if isinstance(content, str) else str(content)
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        KeyError,
        json.JSONDecodeError,
        IndexError,
        TypeError,
    ):
        return None


def analizar_con_llm(input_usuario: str) -> dict[str, Any]:
    """
    Decisión trazable: LLM + validación + coherencia + umbral de confianza,
    o reglas (simulado / fallback_reglas).

    Retorno siempre:
      intencion: str
      tool: str | None
      confianza: float [0,1]
      fuente: "llm" | "simulado" | "fallback_reglas"
    """
    texto = input_usuario or ""
    reglas = analizar_por_reglas(texto)

    def fallback(motivo: str) -> dict[str, Any]:
        out = _empaquetar_reglas("fallback_reglas", reglas)
        out["motivo_fallback"] = motivo
        return out

    if not os.environ.get("OPENROUTER_API_KEY", "").strip():
        return _empaquetar_reglas("simulado", reglas)

    raw = _llamada_openrouter(texto)
    if raw is None:
        return fallback("error_red_o_respuesta_http")

    data = _extraer_json_desde_texto(raw)
    if data is None:
        return fallback("json_invalido_o_vacio")

    procesado = _procesar_respuesta_llm(data, texto)

    if procesado["confianza"] < CONFIDENCE_THRESHOLD:
        out = _empaquetar_reglas("fallback_reglas", reglas)
        out["motivo_fallback"] = "confianza_por_debajo_del_umbral"
        out["confianza_llm_rechazada"] = procesado["confianza"]
        out["intencion_llm_previa"] = procesado["intencion"]
        out["tool_llm_previo"] = procesado["tool"]
        return out

    return {
        "intencion": procesado["intencion"],
        "tool": procesado["tool"],
        "confianza": procesado["confianza"],
        "fuente": "llm",
    }
