from fastapi import APIRouter, Depends, Request

from app.modules.autenticacion.dependencies.usuario_actual import obtener_usuario_actual
from app.modules.ventas_inventario.schemas.pago.pago_request import (
    ConfirmarPagoPruebaRequest,
    CrearCheckoutStripeRequest,
)
from app.modules.ventas_inventario.schemas.pago.pago_response import (
    CheckoutStripeResponse,
    OrdenPagoResponse,
)
from app.modules.ventas_inventario.services.pago_service import (
    confirmar_pago_prueba_service,
    crear_checkout_stripe_service,
    obtener_orden_service,
    webhook_stripe_service,
)

router = APIRouter(prefix="/api/v1/pagos", tags=["Pagos digitales"])


@router.post("/stripe/checkout", response_model=CheckoutStripeResponse)
def crear_checkout_stripe(
    request: CrearCheckoutStripeRequest,
    usuario_actual: dict[str, object] = Depends(obtener_usuario_actual),
) -> CheckoutStripeResponse:
    return crear_checkout_stripe_service(usuario_actual, request)


@router.get("/orden/{orden_id}", response_model=OrdenPagoResponse)
def obtener_orden_pago(
    orden_id: int,
    usuario_actual: dict[str, object] = Depends(obtener_usuario_actual),
) -> OrdenPagoResponse:
    return obtener_orden_service(usuario_actual, orden_id)


@router.post("/stripe/confirmar-prueba/{orden_id}", response_model=OrdenPagoResponse)
def confirmar_pago_prueba(
    orden_id: int,
    request: ConfirmarPagoPruebaRequest,
    usuario_actual: dict[str, object] = Depends(obtener_usuario_actual),
) -> OrdenPagoResponse:
    return confirmar_pago_prueba_service(usuario_actual, orden_id, request.aprobar)


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request) -> dict[str, str]:
    return await webhook_stripe_service(request)
