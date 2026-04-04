"""
Herramientas del agente. Contrato uniforme para todo resultado:

{
    "ok": bool,
    "tool": str,
    "message": str,
    "data": dict | list  # dict por herramienta; lista de fragmentos en buscar_en_pdf
}
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from pdf_rag import buscar_en_corpus, directorio_corpus_defecto, listar_pdfs_corpus


def _envelope(
    ok: bool,
    tool: str,
    message: str,
    data: dict[str, Any] | list[Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] | list[Any] = data if data is not None else {}
    return {
        "ok": ok,
        "tool": tool,
        "message": message,
        "data": payload,
    }


def validar_ruc(ruc: str) -> dict[str, Any]:
    limpio = "".join(c for c in (ruc or "") if c.isdigit())
    if len(limpio) == 11:
        return _envelope(
            True,
            "validar_ruc",
            "RUC válido (formato 11 dígitos).",
            {"ruc": limpio},
        )
    return _envelope(
        False,
        "validar_ruc",
        f"RUC inválido: se esperan 11 dígitos, hay {len(limpio)}.",
        {"ruc": limpio or None},
    )


def leer_pdf(ruta: str) -> dict[str, Any]:
    ruta = (ruta or "").strip()
    if not ruta.lower().endswith(".pdf"):
        return _envelope(
            False,
            "leer_pdf",
            "La ruta no parece un .pdf (simulado).",
            {"ruta": ruta},
        )
    return _envelope(
        True,
        "leer_pdf",
        "PDF leído (simulado).",
        {
            "ruta": ruta,
            "contenido_simulado": "[Texto extraído ficticio del documento]",
        },
    )


def buscar_en_pdf(pregunta: str) -> dict[str, Any]:
    """
    Todos los .pdf en ./corpus/: índice en memoria, embeddings (all-MiniLM-L6-v2), top-5 por coseno.
    """
    pregunta = (pregunta or "").strip()
    root = directorio_corpus_defecto()

    if not root.is_dir():
        return _envelope(
            False,
            "buscar_en_pdf",
            f"No existe la carpeta corpus: {root}",
            [],
        )

    pdfs = listar_pdfs_corpus(root)
    if not pdfs:
        return _envelope(
            False,
            "buscar_en_pdf",
            f"No hay archivos .pdf en {root}",
            [],
        )

    try:
        fragmentos = buscar_en_corpus(pregunta, root)
    except OSError as exc:
        return _envelope(
            False,
            "buscar_en_pdf",
            f"No se pudo leer el corpus: {exc}",
            [],
        )
    except ImportError as exc:
        hint = str(exc) if "sentence-transformers" in str(exc) else str(exc)
        return _envelope(
            False,
            "buscar_en_pdf",
            f"Dependencia de embeddings no disponible: {hint}",
            [],
        )

    if not fragmentos:
        return _envelope(
            False,
            "buscar_en_pdf",
            "El índice del corpus está vacío o no se pudo recuperar ningún fragmento.",
            [],
        )

    data_list: list[dict[str, Any]] = []
    for f in fragmentos:
        item: dict[str, Any] = {
            "texto": f.texto,
            "score": round(float(f.score), 6),
            "archivo": f.archivo,
            "pagina": f.pagina,
            "tipo": f.tipo,
            "chunk_id": f.chunk_id,
            "confidence": round(float(f.confidence), 6),
        }
        if f.titulo:
            item["titulo"] = f.titulo
        if f.pagina_fin != f.pagina:
            item["pagina_fin"] = f.pagina_fin
        if f.articulo:
            item["articulo"] = f.articulo
        if f.numeral:
            item["numeral"] = f.numeral
        if f.inciso:
            item["inciso"] = f.inciso
        data_list.append(item)

    return _envelope(
        True,
        "buscar_en_pdf",
        f"{len(data_list)} fragmentos (coseno + 0.1×keywords, ajuste por tipo de chunk; top {len(data_list)}).",
        data_list,
    )


def calcular_monto(texto: str) -> dict[str, Any]:
    t = texto or ""
    nums = re.findall(r"\d+(?:[.,]\d+)?", t)
    valores = [float(n.replace(",", ".")) for n in nums]
    if not valores:
        return _envelope(
            False,
            "calcular_monto",
            "No se encontraron montos numéricos.",
            {},
        )
    total = round(sum(valores), 2)
    return _envelope(
        True,
        "calcular_monto",
        f"Procesados {len(valores)} valor(es).",
        {"valores": valores, "total": total},
    )


def _resolver_ruta_pdf(ctx: str) -> str:
    """Ruta explícita en el mensaje, variable de entorno o un PDF en corpus (para leer_pdf)."""
    m = re.search(r"[\w./\\:-]+\.pdf\b", ctx or "", re.IGNORECASE)
    if m:
        return m.group(0)
    env = os.environ.get("AGENT_DEFAULT_PDF", "").strip()
    if env:
        return env
    base = Path(__file__).resolve().parent
    for p in sorted((base / "corpus").glob("*.pdf")):
        return str(p)
    return ""


def despachar(nombre: str, contexto_texto: str) -> dict[str, Any]:
    """
    Punto único de invocación desde tool_node.
    `contexto_texto` suele ser el input original del usuario.
    """
    nombre = (nombre or "").strip()
    ctx = contexto_texto or ""

    if nombre == "validar_ruc":
        digitos = re.findall(r"\d+", ctx)
        ruc_src = max(digitos, key=len) if digitos else re.sub(r"\D", "", ctx)
        return validar_ruc(ruc_src or "0")

    if nombre == "leer_pdf":
        m = re.search(r"[\w./\\:-]+\.pdf\b", ctx, re.IGNORECASE)
        ruta = m.group(0) if m else _resolver_ruta_pdf(ctx) or "documento_simulado.pdf"
        return leer_pdf(ruta)

    if nombre == "calcular_monto":
        return calcular_monto(ctx)

    if nombre == "buscar_en_pdf":
        return buscar_en_pdf(ctx)

    return _envelope(
        False,
        nombre or "desconocida",
        f"No hay implementación para la herramienta '{nombre}'.",
        {},
    )
