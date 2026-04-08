"""
Punto de entrada: sesión interactiva del agente o evaluación RAG sin LLM (--rag-eval).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from orchestrator import run_pipeline
from pdf_rag import (
    buscar_en_corpus,
    construir_indice_en_memoria,
    directorio_corpus_defecto,
    listar_pdfs_corpus,
)
from state import AgentState

_SALIDA = frozenset({"salir", "exit", "quit"})


def _ruta_eval_questions_default() -> Path:
    return Path(__file__).resolve().parent / "eval_questions.json"


def _normalizar_nombre_pdf(n: str) -> str:
    return Path(n.replace("\\", "/")).name.strip().lower()


def _intervalos_solapan(
    a_lo: int, a_hi: int, b_lo: int, b_hi: int
) -> bool:
    return not (a_hi < b_lo or a_lo > b_hi)


def _pagina_esperada_cubre_top1(
    esperado: int, margen: int, pagina: int, pagina_fin: int
) -> bool:
    """True si la página esperada (±margen) intersecta el rango del chunk top-1."""
    lo = esperado - margen
    hi = esperado + margen
    return _intervalos_solapan(pagina, pagina_fin, lo, hi)


def ejecutar_eval_rag_benchmark(
    path_json: Path,
    dominio: str | None = None,
    verbose: bool = False,
) -> int:
    """
    Carga eval_questions.json, ejecuta una búsqueda por pregunta y compara top-1
    con archivo_correcto y pagina_aproximada (tolerancia configurable).
    No modifica ranking ni embeddings: solo mide.
    """
    root = directorio_corpus_defecto()
    print("=" * 72)
    print("BENCHMARK RAG — top-1 vs ground truth (eval_questions.json)")
    print("=" * 72)
    print(f"  corpus: {root.resolve()}")
    print(f"  eval:   {path_json.resolve()}")
    if dominio:
        print(f"  dominio: {dominio}")

    if not path_json.is_file():
        print(f"\nERROR: no existe {path_json}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(path_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"\nERROR leyendo JSON: {exc}", file=sys.stderr)
        return 1

    items = payload.get("preguntas") or payload.get("items")
    if not isinstance(items, list) or not items:
        print("\nERROR: JSON sin lista 'preguntas'.", file=sys.stderr)
        return 1

    margen_def = int(payload.get("margen_paginas_default", 2))

    if not root.is_dir():
        print("\nERROR: no existe la carpeta corpus.", file=sys.stderr)
        return 1

    pdfs = listar_pdfs_corpus(root)
    if not pdfs:
        print("\nERROR: no hay PDFs en corpus.", file=sys.stderr)
        return 1

    totales = {"ok": 0, "n": 0, "archivo_ok": 0, "pagina_ok": 0}
    por_cat: dict[str, dict[str, int]] = {}

    print()
    hdr = (
        f"{'#':>3}  {'arch':^3}  {'pag':^3}  {'ok':^3}  "
        f"{'top-1 archivo':<42}  {'pág':^5}  categoria"
    )
    print(hdr)
    print("-" * 120)

    for i, row in enumerate(items, 1):
        if not isinstance(row, dict):
            continue
        pregunta = (row.get("pregunta") or "").strip()
        arch_exp = (row.get("archivo_correcto") or "").strip()
        pag_exp = row.get("pagina_aproximada")
        categoria = (row.get("categoria") or "—").strip()
        margen = int(row.get("margen_paginas", margen_def))

        if not pregunta or not arch_exp or pag_exp is None:
            print(f"{i:3}  SKIP (fila incompleta)")
            continue

        try:
            pag_exp_i = int(pag_exp)
        except (TypeError, ValueError):
            print(f"{i:3}  SKIP pagina_aproximada inválida")
            continue

        totales["n"] += 1
        por_cat.setdefault(categoria, {"ok": 0, "n": 0})
        por_cat[categoria]["n"] += 1

        try:
            fragmentos = buscar_en_corpus(pregunta, root, dominio)
        except Exception as exc:  # noqa: BLE001
            print(f"{i:3}  ERR  buscar_en_corpus: {exc}")
            continue

        if not fragmentos:
            print(
                f"{i:3}  NO   NO   NO   (sin resultados)  "
                f"esperado: {arch_exp[:36]}… p.{pag_exp_i}"
            )
            if verbose:
                print(f"     Q: {pregunta}")
            continue

        fr = fragmentos[0]
        arch_got = _normalizar_nombre_pdf(fr.archivo)
        arch_exp_n = _normalizar_nombre_pdf(arch_exp)
        ok_arch = arch_got == arch_exp_n

        p_lo = min(fr.pagina, fr.pagina_fin)
        p_hi = max(fr.pagina, fr.pagina_fin)
        ok_pag = _pagina_esperada_cubre_top1(
            pag_exp_i, margen, p_lo, p_hi
        )

        ok = ok_arch and ok_pag
        if ok:
            totales["ok"] += 1
            por_cat[categoria]["ok"] += 1
        if ok_arch:
            totales["archivo_ok"] += 1
        if ok_pag:
            totales["pagina_ok"] += 1

        a_mark = "SI" if ok_arch else "NO"
        p_mark = "SI" if ok_pag else "NO"
        o_mark = "SI" if ok else "NO"
        nom = fr.archivo[:42] if len(fr.archivo) <= 42 else fr.archivo[:39] + "..."
        pag_str = f"{fr.pagina}" if fr.pagina_fin == fr.pagina else f"{fr.pagina}-{fr.pagina_fin}"
        print(
            f"{i:3}  {a_mark:^3}  {p_mark:^3}  {o_mark:^3}  "
            f"{nom:<42}  {pag_str:^5}  {categoria}"
        )
        if verbose or not ok:
            print(
                f"     esperado: {arch_exp_n}  p.~{pag_exp_i} (±{margen})"
            )
            if not ok and verbose:
                print(f"     Q: {pregunta}")

    print("-" * 120)
    n = totales["n"]
    if n == 0:
        print("\nNo se evaluó ninguna pregunta.")
        return 1

    pct = 100.0 * totales["ok"] / n
    pct_a = 100.0 * totales["archivo_ok"] / n
    pct_p = 100.0 * totales["pagina_ok"] / n
    print()
    print("RESUMEN")
    print(f"  Preguntas evaluadas: {n}")
    print(
        f"  Top-1 correcto (archivo Y página dentro de tolerancia): "
        f"{totales['ok']}/{n}  ({pct:.1f}%)"
    )
    print(f"  Solo archivo correcto: {totales['archivo_ok']}/{n}  ({pct_a:.1f}%)")
    print(f"  Solo página (intervalo) correcta: {totales['pagina_ok']}/{n}  ({pct_p:.1f}%)")
    print()
    print("Por categoría (acierto completo / total):")
    for cat in sorted(por_cat.keys()):
        d = por_cat[cat]
        nn = d["n"]
        if nn == 0:
            continue
        print(f"  {cat}: {d['ok']}/{nn}  ({100.0 * d['ok'] / nn:.1f}%)")

    print()
    print(
        "Nota: 'página correcta' = solapamiento entre [pagina, pagina_fin] del chunk "
        f"y [esperado ± margen]. Margen por defecto: {margen_def}."
    )
    print("=" * 72)
    return 0

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
    _linea("dominio", fr.dominio if fr.dominio else "(raíz)")
    _linea("tipo_doc", fr.tipo_doc if fr.tipo_doc else "(—)")
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


def ejecutar_eval_rag(
    preguntas: tuple[str, ...] | list[str],
    dominio: str | None = None,
) -> int:
    """
    Carga o genera índice, ejecuta búsqueda semántica+híbrida por cada pregunta.
    Salida: solo fragmentos y metadatos. Sin LLM, sin resumen, sin inferencias.
    """
    root = directorio_corpus_defecto()
    print("=" * 72)
    print("EVALUACIÓN RAG (recuperación únicamente — sin LLM ni interpretación)")
    print("=" * 72)
    _linea("corpus", str(root.resolve()))
    if dominio:
        _linea("filtro dominio (AGENT_RAG_DOMINIO / --dominio)", dominio)

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
            fragmentos = buscar_en_corpus(pregunta, root, dominio)
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Salida RAG detallada (chunk largo, otros hits, chunk_id). Equivale a AGENT_OUTPUT_MODE=verbose.",
    )
    parser.add_argument(
        "--dominio",
        type=str,
        default="",
        help="Con --rag-eval: filtra por dominio (carpeta bajo corpus); incluye siempre 'transversal'. Vacío = global. También: AGENT_RAG_DOMINIO.",
    )
    parser.add_argument(
        "--rag-eval-benchmark",
        action="store_true",
        help=(
            "Carga eval_questions.json: compara top-1 (archivo y página) con ground truth; "
            "muestra % acierto. No cambia el ranking."
        ),
    )
    parser.add_argument(
        "--eval-json",
        type=str,
        default="",
        help="Con --rag-eval-benchmark: ruta al JSON de preguntas (por defecto agent_sandbox/eval_questions.json).",
    )
    args = parser.parse_args()

    if args.verbose:
        os.environ["AGENT_OUTPUT_MODE"] = "verbose"
    else:
        os.environ.setdefault("AGENT_OUTPUT_MODE", "short")

    dom_filtro = (args.dominio or "").strip() or (
        (os.environ.get("AGENT_RAG_DOMINIO") or "").strip() or None
    )

    if args.rag_eval_benchmark:
        path_eval = (
            Path(args.eval_json.strip()).expanduser().resolve()
            if (args.eval_json or "").strip()
            else _ruta_eval_questions_default()
        )
        sys.exit(
            ejecutar_eval_rag_benchmark(
                path_eval,
                dominio=dom_filtro,
                verbose=args.verbose,
            )
        )

    if args.rag_eval:
        if args.pregunta.strip():
            sys.exit(ejecutar_eval_rag((args.pregunta.strip(),), dominio=dom_filtro))
        sys.exit(ejecutar_eval_rag(PREGUNTAS_EVAL_RAG, dominio=dom_filtro))

    print("Agente modular (nodos). Palabras clave: ruc | pdf | monto. Salir: salir\n")
    print(
        "Tip: python main.py --rag-eval  -> prueba RAG sin LLM sobre ./corpus\n"
        "     python main.py --rag-eval-benchmark  -> métricas vs eval_questions.json\n"
    )
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
