"""
Orquestador del motor PASO 4.5 — Fase 1 MVP.

Carga `expediente.json`, valida que sea schema `expediente.v4`, ejecuta las
5 reglas registradas en orden estable, agrega `decision_global` y devuelve
un `DecisionEngineOutput`.

NO escribe `decision_engine_output.json` por sí solo: la función pública
solo retorna el dataclass. Únicamente el CLI con flag `--out` explícito
escribe a disco. Esto preserva la regla "No generar archivos sin
autorización" durante desarrollo y tests.

Determinismo:
  - El orden de `reglas_evaluadas` es el de `cargar_reglas()`.
  - `hallazgos` se ordena por `(regla_id, scope, objeto_id, severidad, explicacion)`.
  - `metadata_corrida` se aísla y puede excluirse vía
    `incluir_metadata_corrida=False` para snapshots reproducibles.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import socket
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

_scripts = str(Path(__file__).resolve().parent.parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from auditoria.reglas import cargar_reglas  # noqa: E402
from modelo.decision_engine_output import (  # noqa: E402
    DecisionEngineOutput,
    Hallazgo,
    MetadataCorrida,
    ResultadoRegla,
    RESULTADO_NO_APLICABLE,
    RESULTADO_OBSERVAR,
    RESULTADO_OK,
    RESULTADO_REVISAR,
)


SCHEMA_INPUT_ESPERADO = "expediente.v4"


class SchemaVersionError(ValueError):
    """Input no es `expediente.v4`. El motor rechaza versiones antiguas."""


def _hash_sha256_archivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit_actual() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


def _decision_global(reglas: list[ResultadoRegla]) -> str:
    if any(r.resultado == RESULTADO_REVISAR for r in reglas):
        return RESULTADO_REVISAR
    if any(r.resultado == RESULTADO_OBSERVAR for r in reglas):
        return RESULTADO_OBSERVAR
    return RESULTADO_OK


def _construir_resumen(reglas: list[ResultadoRegla]) -> dict[str, Any]:
    contadores = {
        RESULTADO_OK: 0,
        RESULTADO_OBSERVAR: 0,
        RESULTADO_REVISAR: 0,
        RESULTADO_NO_APLICABLE: 0,
    }
    for r in reglas:
        contadores[r.resultado] = contadores.get(r.resultado, 0) + 1
    return {
        "n_reglas_definidas": len(reglas),
        "n_reglas_evaluadas": len(reglas),
        "n_reglas_aplicables": len(reglas) - contadores[RESULTADO_NO_APLICABLE],
        "por_severidad": {
            "OK": contadores[RESULTADO_OK],
            "OBSERVAR": contadores[RESULTADO_OBSERVAR],
            "REVISAR": contadores[RESULTADO_REVISAR],
            "NO_APLICABLE": contadores[RESULTADO_NO_APLICABLE],
        },
        "por_regla": {r.regla_id: r.resultado for r in reglas},
    }


def _ordenar_hallazgos(hallazgos: list[Hallazgo]) -> list[Hallazgo]:
    return sorted(
        hallazgos,
        key=lambda h: (
            h.regla_id,
            h.scope,
            h.objeto_id,
            h.severidad or "",
            h.explicacion,
        ),
    )


def evaluar_expediente(
    exp_dir: Path | str,
    *,
    incluir_metadata_corrida: bool = True,
) -> DecisionEngineOutput:
    """Evalúa un expediente.v4 con las 5 reglas MVP.

    Args:
        exp_dir: directorio `control_previo/procesados/<id>/` que contiene
                 `expediente.json`.
        incluir_metadata_corrida: si False, omite `MetadataCorrida` del output
                 (útil para snapshots y tests reproducibles).

    Raises:
        FileNotFoundError: si `expediente.json` no existe en `exp_dir`.
        SchemaVersionError: si `schema_version` ≠ `expediente.v4`.
    """
    exp_dir = Path(exp_dir).resolve()
    json_path = exp_dir / "expediente.json"
    if not json_path.exists():
        raise FileNotFoundError(f"No existe {json_path}")

    expediente = json.loads(json_path.read_text(encoding="utf-8"))
    schema_v = expediente.get("schema_version") or ""
    if schema_v != SCHEMA_INPUT_ESPERADO:
        raise SchemaVersionError(
            f"schema_version={schema_v!r}; se requiere {SCHEMA_INPUT_ESPERADO!r}. "
            f"Regenera el JSON con scripts/consolidador.py antes de auditar."
        )

    sha256 = _hash_sha256_archivo(json_path)
    expediente_id = expediente.get("expediente_id_carpeta") or exp_dir.name or ""

    reglas_evaluadas: list[ResultadoRegla] = []
    todos_hallazgos: list[Hallazgo] = []
    for _regla_id, fn in cargar_reglas():
        regla, hall = fn(expediente)
        reglas_evaluadas.append(regla)
        todos_hallazgos.extend(hall)

    md: MetadataCorrida | None = None
    if incluir_metadata_corrida:
        md = MetadataCorrida(
            engine_run_id=str(uuid.uuid4()),
            engine_run_timestamp_utc=datetime.datetime.now(
                datetime.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            engine_host=socket.gethostname(),
            engine_git_commit=_git_commit_actual(),
        )

    return DecisionEngineOutput(
        expediente_id=expediente_id,
        input_referenciado={
            "expediente_json_path": str(json_path),
            "expediente_json_sha256": sha256,
            "expediente_schema_version": SCHEMA_INPUT_ESPERADO,
        },
        decision_global=_decision_global(reglas_evaluadas),
        resumen=_construir_resumen(reglas_evaluadas),
        reglas_evaluadas=reglas_evaluadas,
        hallazgos=_ordenar_hallazgos(todos_hallazgos),
        metadata_corrida=md,
    )


if __name__ == "__main__":
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="Motor de decisión PASO 4.5 — Fase 1 MVP (lee expediente.json v4)."
    )
    ap.add_argument(
        "exp_dir",
        type=Path,
        help="Ruta a control_previo/procesados/<expediente_id>/",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Si se pasa, escribe el JSON a esta ruta. "
            "Por defecto solo imprime a stdout (no escribe disco)."
        ),
    )
    ap.add_argument(
        "--deterministico",
        action="store_true",
        help="Excluye metadata_corrida (timestamps/uuid/host/git_commit).",
    )
    args = ap.parse_args()

    out = evaluar_expediente(
        args.exp_dir,
        incluir_metadata_corrida=not args.deterministico,
    )
    payload = (
        out.to_dict_deterministic() if args.deterministico else out.to_dict()
    )
    s = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)

    if args.out:
        args.out.write_text(s, encoding="utf-8")
        print(f"[decision_engine] {args.out} ({out.decision_global})")
    else:
        print(s)
