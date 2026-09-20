from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel


class ReservaDetalleResponse(BaseModel):
    id: int
    producto_variante_id: int
    producto_id: int
    producto: str
    categoria: str
    talla: str
    color: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class ReservaResponse(BaseModel):
    id: int
    codigo: str
    cliente_id: int
    cliente: str | None = None
    sucursal_id: int
    sucursal: str
    ciudad: str
    estado: str
    total: Decimal
    fecha_reserva: datetime
    fecha_expiracion: datetime | None = None
    observacion: str | None = None
    detalles: list[ReservaDetalleResponse]
