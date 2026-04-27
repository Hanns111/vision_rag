"""
Modelo de Expediente — schema `expediente.v2`.

Objetivo: representar un expediente consolidado a partir de sus documentos
procesados (extractions/*.json) + metadata.json + validaciones opcionales,
con un bloque dedicado de **resolución de identidad administrativa**
(SINAD, SIAF, EXP, AÑO).

Principios:
  - No inventar datos. Todo campo con evidencia insuficiente → None/vacío.
  - Trazabilidad: cada dato con fuente (archivo + fragmento) cuando existe.
  - Idempotencia: el consolidador puede regenerar este objeto sin efectos.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


SCHEMA_VERSION = "expediente.v4"


@dataclass
class FuenteEvidencia:
    archivo: str
    pagina: int | None = None
    fragmento: str = ""
    regla: str = ""
    tipo_documento: str = ""   # rendicion|solicitud|oficio|factura|... del classifier

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IdCandidato:
    id_canonico: str                      # "SINAD-250235" | "SIAF-2603426" | "EXP-0250235" | "ANIO-2026"
    tipo: str                             # sinad|siaf|exp|anio|prefijo_unidad|planilla|pedido|oficio
    valor_original: str                   # texto tal cual apareció (trazabilidad)
    frecuencia: int                       # total de apariciones en el expediente
    score_total: float
    fuentes: list[FuenteEvidencia] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_canonico": self.id_canonico,
            "tipo": self.tipo,
            "valor_original": self.valor_original,
            "frecuencia": self.frecuencia,
            "score_total": round(self.score_total, 3),
            "fuentes": [f.to_dict() for f in self.fuentes],
        }


@dataclass
class ResolucionId:
    """Identidad administrativa del expediente, determinada por evidencia."""
    expediente_id_carpeta: str                   # inmutable, viene del scan
    expediente_id_detectado: str | None = None   # ganador global por score
    sinad: str | None = None                     # "250235" sin prefijo
    siaf: str | None = None
    anio: str | None = None
    confianza_expediente: float = 0.0
    confianza_sinad: float = 0.0
    confianza_siaf: float = 0.0
    confianza_anio: float = 0.0
    estado_resolucion: str = "BAJA_CONFIANZA"    # OK | CONFLICTO_EXPEDIENTE | BAJA_CONFIANZA
    coincide_con_carpeta: bool = False
    candidatos: list[IdCandidato] = field(default_factory=list)
    observaciones: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "expediente_id_carpeta": self.expediente_id_carpeta,
            "expediente_id_detectado": self.expediente_id_detectado,
            "sinad": self.sinad,
            "siaf": self.siaf,
            "anio": self.anio,
            "confianza_expediente": round(self.confianza_expediente, 3),
            "confianza_sinad": round(self.confianza_sinad, 3),
            "confianza_siaf": round(self.confianza_siaf, 3),
            "confianza_anio": round(self.confianza_anio, 3),
            "estado_resolucion": self.estado_resolucion,
            "coincide_con_carpeta": self.coincide_con_carpeta,
            "candidatos": [c.to_dict() for c in self.candidatos],
            "observaciones": list(self.observaciones),
        }


@dataclass
class Comprobante:
    """Comprobante de pago detectado dentro de un documento (factura/boleta/ticket)."""
    archivo: str                   # nombre del PDF contenedor
    pagina_inicio: int
    pagina_fin: int
    tipo: str                      # factura_electronica | boleta_venta | ticket | desconocido
    ruc: str | None = None
    razon_social: str | None = None
    serie_numero: str | None = None
    fecha: str | None = None       # YYYY-MM-DD
    monto_total: str | None = None
    moneda: str | None = None      # PEN | USD
    monto_igv: str | None = None
    bi_gravado: str | None = None
    op_exonerada: str | None = None
    op_inafecta: str | None = None
    recargo_consumo: str | None = None   # recargo al consumo / servicio 10%
    confianza: float = 0.0
    hash_deduplicacion: str = ""   # (ruc|serie|fecha|monto) o hash(texto[:200])
    texto_resumen: str = ""        # primeros ~300 chars del bloque
    # --- v4: receptor + consistencia tributaria persistida (D-24, PRE-PASO 4.5) ---
    ruc_receptor: str | None = None       # RUC del cliente (UE), extraído por PASO 4.1
    estado_consistencia: str = ""         # OK | DIFERENCIA_LEVE | DIFERENCIA_CRITICA | DATOS_INSUFICIENTES
    tipo_tributario: str = ""             # GRAVADA | EXONERADA | INAFECTA | MIXTA | NO_DETERMINABLE | ""
    detalle_inconsistencia: str = ""      # mensaje legible auditable

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FlujoFinanciero:
    """Agregado monetario a nivel expediente — solo desde evidencia, no inventa."""
    total_detectado: str = "0.00"          # suma de monto_total de comprobantes (moneda mayoritaria)
    moneda: str = ""                        # moneda dominante (PEN|USD|"")
    n_comprobantes: int = 0
    n_facturas: int = 0
    n_boletas: int = 0
    n_tickets: int = 0
    n_desconocidos: int = 0
    inconsistencias: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Expediente:
    """Consolidado del expediente; placeholders para campos v1 (aún no poblados)."""
    expediente_id_carpeta: str
    schema_version: str = SCHEMA_VERSION
    resolucion_id: ResolucionId | None = None
    # --- capas v1 (preparadas, se pueblan en pasos posteriores) ---
    tipo_proceso: str = "indefinido"
    categoria_negocio: str = ""
    estado: str = "EN_PROCESO"
    documentos_archivos: list[str] = field(default_factory=list)
    validaciones: list[dict[str, Any]] = field(default_factory=list)
    # --- v3: comprobantes y flujo financiero ---
    comprobantes: list[Comprobante] = field(default_factory=list)
    flujo_financiero: FlujoFinanciero | None = None
    observaciones: list[str] = field(default_factory=list)
    traza: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "expediente_id_carpeta": self.expediente_id_carpeta,
            "tipo_proceso": self.tipo_proceso,
            "categoria_negocio": self.categoria_negocio,
            "estado": self.estado,
            "resolucion_id": self.resolucion_id.to_dict() if self.resolucion_id else None,
            "documentos_archivos": list(self.documentos_archivos),
            "validaciones": list(self.validaciones),
            "comprobantes": [c.to_dict() for c in self.comprobantes],
            "flujo_financiero": self.flujo_financiero.to_dict() if self.flujo_financiero else None,
            "observaciones": list(self.observaciones),
            "traza": list(self.traza),
        }
