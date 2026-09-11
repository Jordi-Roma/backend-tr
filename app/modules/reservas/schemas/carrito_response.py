from decimal import Decimal

from pydantic import BaseModel


class CarritoItemResponse(BaseModel):
    id: int
    producto_variante_id: int
    producto_id: int
    producto: str
    categoria: str
    talla: str
    color: str
    sucursal_id: int | None = None
    sucursal: str | None = None
    ciudad: str | None = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    stock_disponible: int


class CarritoResponse(BaseModel):
    id: int
    items: list[CarritoItemResponse]
    total: Decimal


class MensajeResponse(BaseModel):
    mensaje: str
