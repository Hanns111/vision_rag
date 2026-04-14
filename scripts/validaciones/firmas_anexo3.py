"""
Validación de firmas en el Anexo 3 (rendición de viáticos MINEDU / SIGA).

Principios:
  - Segregación de funciones: comisionado ≠ jefe_unidad ≠ vb_coordinador.
  - Control jerárquico: si el comisionado coincide con el nombre del bloque
    "Jefe de unidad/órgano" → OBSERVADO (requiere firma del superior; sin base
    jerárquica externa no podemos validar que el superior haya firmado).
  - No inventar: un `nombre` solo se declara cuando hay **DNI o firma digital
    FAU como anchor** en la ventana del rol. Sin anchor → nombre=None, aun
    si la etiqueta del rol está presente.

Entrada: texto ya extraído (OCR/nativo). El módulo NO hace OCR ni CV.

Limitación conocida:
  Las firmas manuscritas (trazo sobre la hoja) no son visibles desde texto;
  solo detectamos el texto asociado al bloque. Si una firma existe pero el
  OCR no reporta DNI/FAU junto al nombre → reportamos INSUFICIENTE_EVIDENCIA
  para ese rol, no CONFORME.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


ESTADO_CONFORME = "CONFORME"
ESTADO_OBSERVADO = "OBSERVADO"
ESTADO_INSUFICIENTE = "INSUFICIENTE_EVIDENCIA"

ROLES = ("comisionado", "jefe_unidad", "vb_coordinador")


@dataclass
class FirmanteDetectado:
    rol: str
    nombre: str | None
    dni: str | None
    regla: str            # id de la regla que detectó la etiqueta
    evidencia: str        # fragmento corto del texto (trazabilidad)
    anchor: str           # "dni" | "fau" | "sin_anchor"


@dataclass
class ValidacionFirmasResult:
    tipo_validacion: str = "firmas_anexo3"
    estado: str = ESTADO_INSUFICIENTE
    errores: list[str] = field(default_factory=list)
    confianza: float = 0.0
    firmantes: list[FirmanteDetectado] = field(default_factory=list)
    nota: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tipo_validacion": self.tipo_validacion,
            "estado": self.estado,
            "errores": list(self.errores),
            "confianza": round(self.confianza, 3),
            "firmantes": [
                {
                    "rol": f.rol,
                    "nombre": f.nombre,
                    "dni": f.dni,
                    "regla": f.regla,
                    "anchor": f.anchor,
                    "evidencia": f.evidencia,
                }
                for f in self.firmantes
            ],
            "nota": self.nota,
        }


# "V° B°" sale degradado en OCR como "V� B�", "V* B*", "Vo Bo".
_RE_VB = r"V\s*[°o\*\.\�]*\s*\.?\s*B\s*[°o\*\.\�]*\s*\.?"

_ETIQUETAS: dict[str, list[tuple[str, str]]] = {
    "comisionado": [
        # Sr(a): es el anchor más confiable en planillas/anexos SIGA (va seguido del nombre).
        (rf"Sr\(a\)\s*:", "etiqueta_sr_a_siga"),
        (rf"FIRMA\s+COMISIONAD[OA]", "etiqueta_firma_comisionado"),
        (rf"^\s*COMISIONAD[OA]\s*$", "etiqueta_comisionado_sola"),
    ],
    "jefe_unidad": [
        (rf"{_RE_VB}\s*DE\s*JEFE\s+DE\s+[ÓO\�]RGANO\s+O\s+UNIDAD", "etiqueta_vb_jefe_organo"),
        (rf"{_RE_VB}\s*(?:DEL?\s*)?JEFE\s+DE\s+UNIDAD", "etiqueta_vb_jefe_unidad"),
        (rf"JEFE\s+(?:DE\s+)?(?:[ÓO\�]RGANO|UNIDAD|INMEDIATO)", "etiqueta_jefe_sin_vb"),
    ],
    "vb_coordinador": [
        (rf"{_RE_VB}\s*(?:DEL?\s*)?COORDINADOR\s+ADMINISTRATIVO", "etiqueta_vb_coordinador"),
        (rf"COORDINADOR\s+ADMINISTRATIVO", "etiqueta_coordinador_admin"),
        (rf"RESPONSABLE\s+ADMINISTRATIVO", "etiqueta_responsable_admin"),
    ],
}

_VENTANA_CHARS = 500

# Palabras que NO pueden ser parte de un nombre propio (etiquetas SIGA, formularios, etc.)
_PALABRAS_NO_NOMBRE = {
    "COMISIONADO", "COMISIONADA", "COMISIONADOS", "FIRMA", "FIRMAS", "FIRMANTE",
    "JEFE", "JEFA", "ORGANO", "ÓRGANO", "UNIDAD", "UNIDADES", "INMEDIATO",
    "COORDINADOR", "COORDINADORA", "ADMINISTRATIVO", "ADMINISTRATIVA",
    "RESPONSABLE", "VISTO", "BUENO", "SELLO", "CARGO",
    "DIRECCION", "DIRECCIÓN", "DIRECTOR", "DIRECTORA",
    "MINISTERIO", "MINEDU", "PROGRAMA", "EDUCACION", "EDUCACIÓN", "BASICA", "BÁSICA", "PARA", "TODOS",
    "FECHA", "HORA", "LUGAR", "DNI", "RUC", "SINAD", "SIAF", "SIGA",
    "TAREA", "PROGRAMADA", "EJECUTADA", "DESPLAZAMIENTO",
    "LIMA", "PERU", "PERÚ", "GRE", "UGEL", "DRE",
    "TOTAL", "MONTO", "ANEXO", "PAGE", "DIA", "DÍA",
    "SISTEMA", "INTEGRADO", "GESTION", "GESTIÓN", "MODULO", "MÓDULO",
    "TESORERIA", "TESORERÍA", "VERSION", "VERSIÓN", "PAGINA", "PÁGINA",
    "CERTIFICACION", "CERTIFICACIÓN", "CREDITO", "CRÉDITO", "PRESUPUESTARIO", "PRESUPUESTARIA",
    "RECURSOS", "ORDINARIOS", "GASTOS", "CORRIENTES", "BIENES", "SERVICIOS",
    "VIAJES", "DOMESTICOS", "DOMÉSTICOS", "PASAJES", "TRANSPORTE", "VIATICOS", "VIÁTICOS",
    "ASIGNACIONES", "COMISION", "COMISIÓN", "SERVICIO",
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
    "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
    "APROBADO", "ESTADO", "NOTA", "DOCUMENTO", "MEMORANDUM",
    "APLICACION", "APLICACIÓN", "INSTRUMENTOS", "RECOJO", "INFORMACION", "INFORMACIÓN",
    "COMITE", "COMITÉ", "EVALUACION", "EVALUACIÓN", "DESEMPEÑO", "DESEMPENO",
    "DIRECTIVOS", "DATOS", "GENERALES",
    "CENTINELA", "CERRO", "URB", "BORJA", "MASIAS", "MASÍAS",
    "TIPO", "CONTRIBUYENTE", "NATURAL", "NEGOCIO",
    "NOMBRE", "NOMBRES", "COMERCIAL", "INSCRIPCION", "INSCRIPCIÓN",
    "RENDICION", "RENDICIÓN", "CUENTAS", "POR", "DEL", "DE", "LA", "EL", "LOS", "LAS",
    "CON", "SIN", "DESDE", "HASTA", "PARA",
    "ESCALA", "FUNCIONARIOS", "EMPLEADOS", "CENTRO", "COSTO",
    "IDENTIFICACION", "IDENTIFICACIÓN", "MOTIVO", "VIAJE",
    "DECLARACION", "DECLARACIÓN", "JURADA", "DOMICILIO", "SOLES", "PEN", "USD",
    "PEDIDO", "NRO", "AHORROS", "CUENTA",
    "FIRMADO", "FIRNADO", "DIGITALMENTE", "DIGITAL",
    "MOTIVE", "MOTIVO", "DOY", "FAU", "SOFT", "ENCARGO",
    "AUTORIZADA", "PAGO",
}

_RE_DNI = re.compile(r"\bDNI\s*N?[°\.ºo]?\s*[:\-]?\s*(\d{7,9})\b", re.I)
_RE_FAU = re.compile(
    r"Firmado\s+digitalmente\s+por\s*:?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][^\n]{5,80})",
    re.I,
)

# Patrones inline donde nombre y anchor están adyacentes (≤60 chars entre ellos).
# El nombre crudo se filtra después por `_limpiar_a_nombre`.
_RE_NOMBRE_ANTES_DNI = re.compile(
    r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ'\s,]{8,80}?)"
    r"\s*(?:,\s*con\s+|\s*,\s*|\s+)"
    r"DNI\s*N?[°\.ºo]?\s*[:\-]?\s*(\d{7,9})",
    re.IGNORECASE,
)
_RE_DNI_ANTES_NOMBRE = re.compile(
    r"DNI\s*N?[°\.ºo]?\s*[:\-]?\s*(\d{7,9})"
    r"\s*[\-,]?\s*"
    r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ'\s]{8,80})",
    re.IGNORECASE,
)
_RE_SR_A_NOMBRE = re.compile(
    r"Sr\(a\)\s*:\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ'\s]{8,80})",
    re.IGNORECASE,
)


def _normalizar(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" ,.:;-_|").upper()
    return s


def _tokens_nombre(s: str) -> list[str]:
    """Tokens de ≥4 letras, sin palabras funcionales (etiquetas SIGA, comunes)."""
    s = _normalizar(s)
    toks = re.findall(r"[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ']{3,}", s)
    return [t for t in toks if t not in _PALABRAS_NO_NOMBRE]


def _es_nombre_valido(cand: str) -> bool:
    """Nombre propio ≈ ≥3 tokens ≥4 chars no-funcionales (ej. CHAVEZ TERRONES LILIANA)."""
    toks = _tokens_nombre(cand)
    return len(toks) >= 3


def _limpiar_a_nombre(cand: str) -> str | None:
    toks = _tokens_nombre(cand)
    if len(toks) < 3:
        return None
    return " ".join(toks[:5])


def _mismo_nombre(a: str | None, b: str | None) -> bool:
    """Coincidencia difusa por intersección de tokens largos."""
    if not a or not b:
        return False
    ta = set(_tokens_nombre(a))
    tb = set(_tokens_nombre(b))
    if not ta or not tb:
        return False
    inter = ta & tb
    return len(inter) >= 2 or len(inter) / min(len(ta), len(tb)) >= 0.6


def _buscar_anchor(texto: str, v_start: int, v_end: int) -> tuple[str | None, str | None, str]:
    """
    Busca en la ventana un anchor válido (DNI adyacente a nombre, o FAU).
    Devuelve (nombre, dni, tipo_anchor). Sin anchor adyacente → (None, None, 'sin_anchor').
    """
    ventana = texto[v_start:v_end]

    # 1) NOMBRE ... DNI N° NNNNNNNN  (adyacentes, ≤60 chars entre ellos)
    m = _RE_NOMBRE_ANTES_DNI.search(ventana)
    if m:
        nombre = _limpiar_a_nombre(m.group(1))
        if nombre:
            return nombre, m.group(2), "nombre_dni_adyacentes"

    # 2) DNI NNNNNNNN - NOMBRE
    m = _RE_DNI_ANTES_NOMBRE.search(ventana)
    if m:
        nombre = _limpiar_a_nombre(m.group(2))
        if nombre:
            return nombre, m.group(1), "dni_nombre_adyacentes"

    # 3) "Sr(a): NOMBRE" (anchor típico SIGA) + DNI aparte (opcional)
    m = _RE_SR_A_NOMBRE.search(ventana)
    if m:
        nombre = _limpiar_a_nombre(m.group(1))
        if nombre:
            dni = None
            md = _RE_DNI.search(ventana)
            if md:
                dni = md.group(1)
            return nombre, dni, "sr_a_nombre"

    # 4) Firma digital FAU
    m = _RE_FAU.search(ventana)
    if m:
        nombre = _limpiar_a_nombre(m.group(1))
        if nombre:
            return nombre, None, "fau"

    # 5) Hay DNI pero sin nombre adyacente → reportar DNI sin nombre
    m = _RE_DNI.search(ventana)
    if m:
        return None, m.group(1), "dni_sin_nombre_adyacente"

    return None, None, "sin_anchor"


def _detectar_rol(rol: str, texto: str) -> FirmanteDetectado | None:
    """Busca la primera etiqueta del rol y extrae nombre/dni con anchor obligatorio."""
    for patron, regla_id in _ETIQUETAS[rol]:
        try:
            rx = re.compile(patron, re.IGNORECASE | re.MULTILINE)
        except re.error:
            continue
        m = rx.search(texto)
        if not m:
            continue
        v_start = max(0, m.start() - _VENTANA_CHARS)
        v_end = min(len(texto), m.end() + _VENTANA_CHARS)
        nombre, dni, anchor = _buscar_anchor(texto, v_start, v_end)
        evid_raw = texto[max(0, m.start() - 60) : m.end() + 60]
        evid = re.sub(r"\s+", " ", evid_raw).strip()[:200]
        return FirmanteDetectado(
            rol=rol,
            nombre=nombre,
            dni=dni,
            regla=regla_id,
            evidencia=evid,
            anchor=anchor,
        )
    return None


def _confianza(detectados: dict[str, FirmanteDetectado | None]) -> float:
    completos = sum(
        1 for f in detectados.values() if f and f.nombre and (f.dni or f.anchor == "fau")
    )
    con_etiqueta = sum(1 for f in detectados.values() if f is not None)
    score = 0.3 * completos + 0.05 * max(0, con_etiqueta - completos)
    return max(0.0, min(1.0, round(score, 3)))


def validar(texto: str) -> ValidacionFirmasResult:
    """Devuelve resultado normalizado (no lanza excepciones sobre input vacío)."""
    texto = texto or ""
    if not texto.strip():
        return ValidacionFirmasResult(
            estado=ESTADO_INSUFICIENTE,
            errores=["texto_vacio"],
            confianza=0.0,
            nota="sin_texto_para_analizar",
        )

    detectados: dict[str, FirmanteDetectado | None] = {
        rol: _detectar_rol(rol, texto) for rol in ROLES
    }
    firmantes = [f for f in detectados.values() if f is not None]

    if all(f is None for f in detectados.values()):
        return ValidacionFirmasResult(
            estado=ESTADO_INSUFICIENTE,
            errores=["sin_bloque_firmas_anexo3"],
            confianza=0.0,
            nota="no_se_hallaron_etiquetas_de_rol",
        )

    errores: list[str] = []
    for rol, f in detectados.items():
        if f is None:
            errores.append(f"rol_no_detectado:{rol}")
        elif not f.nombre:
            errores.append(f"nombre_ilegible:{rol}:anchor={f.anchor}")

    com = detectados.get("comisionado")
    jef = detectados.get("jefe_unidad")
    vb_ = detectados.get("vb_coordinador")

    if com and jef and com.nombre and jef.nombre and _mismo_nombre(com.nombre, jef.nombre):
        errores.append("segregacion_funciones:comisionado_y_jefe_coinciden_requiere_superior")
    if com and vb_ and com.nombre and vb_.nombre and _mismo_nombre(com.nombre, vb_.nombre):
        errores.append("segregacion_funciones:comisionado_y_vb_coinciden")
    if jef and vb_ and jef.nombre and vb_.nombre and _mismo_nombre(jef.nombre, vb_.nombre):
        errores.append("segregacion_funciones:jefe_y_vb_coinciden")

    if com is None or not com.nombre:
        # sin comisionado con nombre, no hay base para validar el expediente
        estado = ESTADO_INSUFICIENTE
    elif any(e.startswith("segregacion_funciones") for e in errores):
        estado = ESTADO_OBSERVADO
    elif any(e.startswith("rol_no_detectado") or e.startswith("nombre_ilegible") for e in errores):
        estado = ESTADO_OBSERVADO
    else:
        estado = ESTADO_CONFORME

    return ValidacionFirmasResult(
        estado=estado,
        errores=errores,
        confianza=_confianza(detectados),
        firmantes=firmantes,
        nota=f"detectados={sum(1 for f in detectados.values() if f)}/3",
    )
