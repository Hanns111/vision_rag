"""
Punto de entrada: sesión interactiva del agente o evaluación RAG sin LLM (--rag-eval).
"""

from __future__ import annotations

import argparse
import sys

from orchestrator import run_pipeline
from pdf_rag import (
    buscar_en_corpus,
    construir_indice_en_memoria,
    directorio_corpus_defecto,
    listar_pdfs_corpus,
)
from state import AgentState

_SALIDA = frozenset({"salir", "exit", "quit"})

# Casos mínimos solicitados (solo recuperación; sin resumen ni interpretación).
PREGUNTAS_EVAL_RAG = (
    "¿Qué dice la norma sobre viáticos?",
    "¿Cuál es el artículo que regula la rendición de gastos?",
    "¿Qué requisitos se mencionan para comprobantes de pago?",
)


def _linea(label: str, valor: object) -> None:
    print(f"  {label}: {valor}")


def _imprimir_fragmento_eval(rank: int, fr) -> None:
    """fr: Fragmento de pdf_rag."""
    print(f"\n  --- Resultado #{rank} ---")
    _linea("archivo", fr.archivo)
    if fr.pagina_fin != fr.pagina:
        _linea("página", f"{fr.pagina}–{fr.pagina_fin}")
    else:
        _linea("página", fr.pagina)
    _linea("chunk_id", fr.chunk_id)
    _linea("tipo", fr.tipo)
    if fr.titulo:
        _linea("titulo_struct", fr.titulo)
    _linea("confidence", fr.confidence)
    _linea("score", fr.score)
    print("  citas detectadas (regex sobre el chunk, no verificación jurídica):")
    _linea("    artículo", fr.articulo if fr.articulo else "(ninguna)")
    _linea("    numeral", fr.numeral if fr.numeral else "(ninguna)")
    _linea("    inciso", fr.inciso if fr.inciso else "(ninguna)")
    print("\n  FRAGMENTO:")
    print("  " + "-" * 60)
    # Texto tal cual recuperado; sin envolver en interpretación.
    for line in (fr.texto or "").splitlines():
        print(f"  {line}")
    print("  " + "-" * 60)


def ejecutar_eval_rag(preguntas: tuple[str, ...] | list[str]) -> int:
    """
    Carga o genera índice, ejecuta búsqueda semántica+híbrida por cada pregunta.
    Salida: solo fragmentos y metadatos. Sin LLM, sin resumen, sin inferencias.
    """
    root = directorio_corpus_defecto()
    print("=" * 72)
    print("EVALUACIÓN RAG (recuperación únicamente — sin LLM ni interpretación)")
    print("=" * 72)
    _linea("corpus", str(root.resolve()))

    if not root.is_dir():
        print("\nERROR: no existe la carpeta corpus.", file=sys.stderr)
        return 1

    pdfs = listar_pdfs_corpus(root)
    if not pdfs:
        print("\nERROR: no hay PDFs en corpus.", file=sys.stderr)
        return 1

    try:
        indice = construir_indice_en_memoria(root)
    except ImportError as exc:
        print(f"\nERROR dependencias: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"\nERROR I/O índice/corpus: {exc}", file=sys.stderr)
        return 1

    print(f"\nÍndice listo: {len(indice)} chunk(s) (cargado desde disco si aplica o reconstruido).")
    print(f"PDFs en corpus: {len(pdfs)}")

    for i, pregunta in enumerate(preguntas, 1):
        print("\n" + "=" * 72)
        print(f"CASO {i} — PREGUNTA (texto literal)")
        print("=" * 72)
        print(pregunta)

        try:
            fragmentos = buscar_en_corpus(pregunta, root)
        except Exception as exc:  # noqa: BLE001 — informar fallo de evaluación
            print(f"\nERROR en búsqueda: {exc}", file=sys.stderr)
            return 1

        if not fragmentos:
            print("\n  (sin fragmentos recuperados para esta pregunta)")
            continue

        print(f"\nFragmentos recuperados (top {len(fragmentos)}):")
        for r, fr in enumerate(fragmentos, 1):
            _imprimir_fragmento_eval(r, fr)

    print("\n" + "=" * 72)
    print("Fin evaluación. Validación manual: contrastar FRAGMENTO con el PDF (archivo/página).")
    print("=" * 72)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agente modular o evaluación RAG del corpus (sin LLM en --rag-eval).",
    )
    parser.add_argument(
        "--rag-eval",
        action="store_true",
        help="Ejecuta solo recuperación sobre el corpus (índice JSON/PDF); imprime citas detectadas y texto crudo.",
    )
    parser.add_argument(
        "--pregunta",
        type=str,
        default="",
        help="Con --rag-eval: una sola pregunta; si se omite, se usan las 3 preguntas de prueba predefinidas.",
    )
    args = parser.parse_args()

    if args.rag_eval:
        if args.pregunta.strip():
            sys.exit(ejecutar_eval_rag((args.pregunta.strip(),)))
        sys.exit(ejecutar_eval_rag(PREGUNTAS_EVAL_RAG))

    print("Agente modular (nodos). Palabras clave: ruc | pdf | monto. Salir: salir\n")
    print("Tip: python main.py --rag-eval  → prueba RAG sin LLM sobre ./corpus\n")
    try:
        while True:
            linea = input("Consulta: ").strip()
            if linea.lower() in _SALIDA:
                print("Adiós.")
                break
            estado_final = run_pipeline(AgentState.desde_entrada(linea))
            print(estado_final.respuesta_final or "")
            print()
    except (EOFError, KeyboardInterrupt):
        print("\nAdiós.")


if __name__ == "__main__":
    main()
