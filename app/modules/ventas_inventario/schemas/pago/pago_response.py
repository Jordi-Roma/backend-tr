from decimal import Decimal
from pydantic import BaseModel


class CheckoutStripeResponse(BaseModel):
    orden_id: int
    venta_id: int
    estado: str
    checkout_url: str


class OrdenPagoResponse(BaseModel):
    orden_id: int
    venta_id: int
    cliente_id: int | None = None
    monto_total: Decimal
    moneda: str
    metodo: str
    estado: str
    proveedor: str
    checkout_url: str | None = None
    proveedor_session_id: str | None = None
    fecha_pago: str | None = None
