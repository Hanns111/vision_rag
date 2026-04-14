"""
Generador del Excel de validación humana.

- Entrada: lista de `DocumentoValidacion` (una por archivo) + lista de `ExpedienteValidacion`.
- Salida: `data/piloto_ocr/metrics/validacion_expedientes.xlsx`, 3 hojas:
    * documentos  → una fila por archivo (columnas de sistema + columnas humanas vacías)
    * expedientes → resumen por expediente_id
    * errores     → subconjunto de documentos con estado_procesamiento = error
- Upsert por (expediente_id, archivo): si la fila ya existe, actualiza solo las
  columnas de sistema y preserva lo que el humano haya escrito.

Columnas de sistema: se REESCRIBEN en cada export.
Columnas humanas (tipo_correcto, monto_correcto, fecha_correcta, ruc_correcto,
observaciones, validacion_final): nunca se sobrescriben si ya tienen valor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DocumentoValidacion:
    expediente_id: str
    archivo: str
    ruta_origen: str
    tipo_documento_detectado: str
    confianza_tipo: float
    monto_detectado: str | None
    fecha_detectada: str | None
    ruc_detectado: str | None
    razon_social_detectada: str | None
    numero_documento_detectado: str | None
    tipo_gasto_detectado: str | None
    texto_extraido_resumen: str
    estado_procesamiento: str  # "ok" | "bajo_confianza" | "error"
    nota_sistema: str = ""     # mensajes internos (overrides, errores, etc.)
    # --- Validación normativa: firmas Anexo 3 (opcional; N/A si no es rendición) ---
    validacion_firmas: str = ""       # "firmas_anexo3" | "" (no aplica)
    estado_firmas: str = ""           # CONFORME | OBSERVADO | INSUFICIENTE_EVIDENCIA | ""
    errores_firmas: str = ""          # lista separada por "; "
    confianza_firmas: float | str = ""


@dataclass
class ExpedienteValidacion:
    expediente_id: str
    ruta_origen: str
    ruta_destino: str
    n_documentos: int
    n_ok: int
    n_bajo_confianza: int
    n_error: int
    tipos_detectados: str       # lista separada por coma
    fecha_ingesta: str


_COLS_SISTEMA_DOC = [
    "expediente_id",
    "archivo",
    "ruta_origen",
    "tipo_documento_detectado",
    "confianza_tipo",
    "monto_detectado",
    "fecha_detectada",
    "ruc_detectado",
    "razon_social_detectada",
    "numero_documento_detectado",
    "tipo_gasto_detectado",
    "texto_extraido_resumen",
    "estado_procesamiento",
    "nota_sistema",
    # validación normativa firmas Anexo 3
    "validacion_firmas",
    "estado_firmas",
    "errores_firmas",
    "confianza_firmas",
]
_COLS_HUMANAS_DOC = [
    "tipo_correcto",
    "monto_correcto",
    "fecha_correcta",
    "ruc_correcto",
    "observaciones",
    "validacion_final",
]
_COLS_DOC = _COLS_SISTEMA_DOC + _COLS_HUMANAS_DOC

_COLS_EXPEDIENTES = [
    "expediente_id",
    "ruta_origen",
    "ruta_destino",
    "n_documentos",
    "n_ok",
    "n_bajo_confianza",
    "n_error",
    "tipos_detectados",
    "fecha_ingesta",
]


def _asdict_doc(d: DocumentoValidacion) -> dict[str, Any]:
    return {
        "expediente_id": d.expediente_id,
        "archivo": d.archivo,
        "ruta_origen": d.ruta_origen,
        "tipo_documento_detectado": d.tipo_documento_detectado,
        "confianza_tipo": d.confianza_tipo,
        "monto_detectado": d.monto_detectado,
        "fecha_detectada": d.fecha_detectada,
        "ruc_detectado": d.ruc_detectado,
        "razon_social_detectada": d.razon_social_detectada,
        "numero_documento_detectado": d.numero_documento_detectado,
        "tipo_gasto_detectado": d.tipo_gasto_detectado,
        "texto_extraido_resumen": d.texto_extraido_resumen,
        "estado_procesamiento": d.estado_procesamiento,
        "nota_sistema": d.nota_sistema,
        "validacion_firmas": d.validacion_firmas,
        "estado_firmas": d.estado_firmas,
        "errores_firmas": d.errores_firmas,
        "confianza_firmas": d.confianza_firmas,
    }


def _asdict_exp(e: ExpedienteValidacion) -> dict[str, Any]:
    return {
        "expediente_id": e.expediente_id,
        "ruta_origen": e.ruta_origen,
        "ruta_destino": e.ruta_destino,
        "n_documentos": e.n_documentos,
        "n_ok": e.n_ok,
        "n_bajo_confianza": e.n_bajo_confianza,
        "n_error": e.n_error,
        "tipos_detectados": e.tipos_detectados,
        "fecha_ingesta": e.fecha_ingesta,
    }


def _cargar_filas_existentes(
    path: Path, sheet: str, cols: list[str], key_cols: tuple[str, ...]
) -> dict[tuple, dict[str, Any]]:
    """Lee el xlsx si existe y devuelve {clave: fila_completa}. Clave = tupla de key_cols."""
    if not path.exists():
        return {}
    from openpyxl import load_workbook

    wb = load_workbook(path)
    if sheet not in wb.sheetnames:
        return {}
    ws = wb[sheet]
    headers = [c.value for c in ws[1]] if ws.max_row >= 1 else []
    if not headers:
        return {}
    out: dict[tuple, dict[str, Any]] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        rec = {h: v for h, v in zip(headers, row) if h}
        if not rec:
            continue
        key = tuple(rec.get(k) for k in key_cols)
        if all(k is not None for k in key):
            out[key] = rec
    return out


def _escribir_hoja(
    wb: Any, sheet: str, cols: list[str], filas: list[dict[str, Any]]
) -> None:
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    if sheet in wb.sheetnames:
        del wb[sheet]
    ws = wb.create_sheet(sheet)
    ws.append(cols)

    header_fill = PatternFill("solid", fgColor="305496")
    header_font = Font(bold=True, color="FFFFFF")
    human_fill = PatternFill("solid", fgColor="FFF2CC")  # amarillo suave

    for i, col in enumerate(cols, start=1):
        c = ws.cell(row=1, column=i)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # filas
    for row_idx, f in enumerate(filas, start=2):
        for i, col in enumerate(cols, start=1):
            v = f.get(col)
            c = ws.cell(row=row_idx, column=i, value=v)
            if col in _COLS_HUMANAS_DOC:
                c.fill = human_fill
            if col == "texto_extraido_resumen":
                c.alignment = Alignment(wrap_text=True, vertical="top")

    # anchos de columna aproximados
    anchos = {
        "expediente_id": 26,
        "archivo": 50,
        "ruta_origen": 60,
        "tipo_documento_detectado": 20,
        "confianza_tipo": 14,
        "monto_detectado": 16,
        "fecha_detectada": 14,
        "ruc_detectado": 16,
        "razon_social_detectada": 30,
        "numero_documento_detectado": 22,
        "tipo_gasto_detectado": 20,
        "texto_extraido_resumen": 60,
        "estado_procesamiento": 18,
        "nota_sistema": 40,
        "validacion_firmas": 18,
        "estado_firmas": 22,
        "errores_firmas": 40,
        "confianza_firmas": 16,
        "tipo_correcto": 18,
        "monto_correcto": 14,
        "fecha_correcta": 14,
        "ruc_correcto": 16,
        "observaciones": 40,
        "validacion_final": 18,
        "ruta_destino": 60,
        "n_documentos": 14,
        "n_ok": 10,
        "n_bajo_confianza": 16,
        "n_error": 10,
        "tipos_detectados": 30,
        "fecha_ingesta": 24,
    }
    for i, col in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = anchos.get(col, 20)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def exportar_excel(
    xlsx_path: Path | str,
    documentos: list[DocumentoValidacion],
    expedientes: list[ExpedienteValidacion],
) -> Path:
    """Genera / actualiza el Excel preservando columnas humanas existentes."""
    from openpyxl import Workbook, load_workbook

    xlsx_path = Path(xlsx_path).resolve()
    xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    key_cols = ("expediente_id", "archivo")
    prev = _cargar_filas_existentes(xlsx_path, "documentos", _COLS_DOC, key_cols)

    nuevas_docs: list[dict[str, Any]] = []
    claves_actualizadas: set[tuple] = set()
    for d in documentos:
        fila = _asdict_doc(d)
        # preservar columnas humanas si existían
        key = (d.expediente_id, d.archivo)
        if key in prev:
            for col in _COLS_HUMANAS_DOC:
                v = prev[key].get(col)
                if v not in (None, ""):
                    fila[col] = v
        for col in _COLS_HUMANAS_DOC:
            fila.setdefault(col, None)
        nuevas_docs.append(fila)
        claves_actualizadas.add(key)

    # conservar filas previas que NO se volvieron a procesar (otros expedientes)
    for key, rec in prev.items():
        if key in claves_actualizadas:
            continue
        fila = {col: rec.get(col) for col in _COLS_DOC}
        nuevas_docs.append(fila)

    # errores = subset
    filas_errores = [f for f in nuevas_docs if f.get("estado_procesamiento") == "error"]

    if xlsx_path.exists():
        wb = load_workbook(xlsx_path)
    else:
        wb = Workbook()
        # eliminar sheet por defecto que viene vacío
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

    _escribir_hoja(wb, "documentos", _COLS_DOC, nuevas_docs)
    _escribir_hoja(wb, "expedientes", _COLS_EXPEDIENTES, [_asdict_exp(e) for e in expedientes])
    _escribir_hoja(wb, "errores", _COLS_DOC, filas_errores)

    # ordenar pestañas
    orden = ["documentos", "expedientes", "errores"]
    wb._sheets = [wb[n] for n in orden if n in wb.sheetnames]
    wb.save(xlsx_path)
    return xlsx_path
