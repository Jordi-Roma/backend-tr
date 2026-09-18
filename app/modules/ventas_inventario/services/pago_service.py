import os
from decimal import Decimal

from fastapi import HTTPException, Request, status

from app.modules.ventas_inventario.repositories import pago_repository as repo
from app.modules.ventas_inventario.schemas.pago.pago_request import CrearCheckoutStripeRequest
from app.modules.ventas_inventario.schemas.pago.pago_response import CheckoutStripeResponse, OrdenPagoResponse


def crear_checkout_stripe_service(usuario_actual: dict[str, object], request: CrearCheckoutStripeRequest) -> CheckoutStripeResponse:
    cliente_id = _cliente_id_obligatorio(usuario_actual)
    try:
        orden = repo.crear_orden_desde_carrito(cliente_id, int(usuario_actual["id"]), request.sucursal_id)
        session = _crear_session_stripe(orden)
        orden = repo.actualizar_checkout_stripe(
            int(orden["id"]),
            str(session["id"]),
            str(session["url"]),
            session.get("payment_intent"),
        )
        return _checkout_response(orden)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


def obtener_orden_service(usuario_actual: dict[str, object], orden_id: int) -> OrdenPagoResponse:
    orden = repo.obtener_orden_pago(orden_id)
    if orden is None:
        raise HTTPException(status_code=404, detail="Orden de pago no encontrada.")
    _validar_acceso_orden(usuario_actual, orden)
    return _orden_response(orden)


async def webhook_stripe_service(request: Request) -> dict[str, str]:
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        import stripe
    except ModuleNotFoundError as error:
        raise HTTPException(status_code=503, detail="La dependencia stripe no esta instalada.") from error

    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, signature, endpoint_secret)
        except Exception as error:
            raise HTTPException(status_code=400, detail="Webhook de Stripe invalido.") from error
    else:
        event = await request.json()

    tipo = event.get("type")
    data = event.get("data", {}).get("object", {})
    if tipo == "checkout.session.completed":
        session_id = data.get("id")
        if session_id:
            orden = repo.obtener_orden_por_session(session_id)
            if orden:
                repo.marcar_orden_pagada(int(orden["id"]))
    elif tipo == "checkout.session.expired":
        session_id = data.get("id")
        if session_id and (orden := repo.obtener_orden_por_session(session_id)):
            repo.marcar_orden_no_pagada(int(orden["id"]), "EXPIRADO", "CANCELADA")
    elif tipo == "payment_intent.payment_failed":
        payment_intent = data.get("id")
        if payment_intent:
            # Stripe normalmente relaciona el fallo con la sesion; se deja como evento aceptado.
            pass
    return {"status": "ok"}


def confirmar_pago_prueba_service(usuario_actual: dict[str, object], orden_id: int, aprobar: bool) -> OrdenPagoResponse:
    orden = repo.obtener_orden_pago(orden_id)
    if orden is None:
        raise HTTPException(status_code=404, detail="Orden de pago no encontrada.")
    _validar_acceso_orden(usuario_actual, orden)
    try:
        if aprobar:
            return _orden_response(repo.marcar_orden_pagada(orden_id, int(usuario_actual["id"])))
        return _orden_response(repo.marcar_orden_no_pagada(orden_id, "RECHAZADO", "RECHAZADA"))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _crear_session_stripe(orden: dict) -> dict:
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
    if not secret_key:
        raise HTTPException(status_code=503, detail="STRIPE_SECRET_KEY no esta configurada en el backend.")
    try:
        import stripe
    except ModuleNotFoundError as error:
        raise HTTPException(status_code=503, detail="La dependencia stripe no esta instalada.") from error

    stripe.api_key = secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[_line_item(item) for item in orden["items"]],
        success_url=f"{frontend_url}/pago/resultado?orden_id={orden['id']}&estado=success",
        cancel_url=f"{frontend_url}/pago/cancelado?orden_id={orden['id']}&estado=cancel",
        metadata={"orden_id": str(orden["id"]), "venta_id": str(orden["venta_id"])},
    )
    return {"id": session.id, "url": session.url, "payment_intent": session.payment_intent}


def _line_item(item: dict) -> dict:
    precio = Decimal(item["precio_unitario"])
    return {
        "quantity": int(item["cantidad"]),
        "price_data": {
            "currency": "bob",
            "unit_amount": int((precio * 100).quantize(Decimal("1"))),
            "product_data": {
                "name": str(item["producto"]),
                "description": f"{item['categoria']} - {item['talla']} / {item['color']}",
            },
        },
    }


def _cliente_id_obligatorio(usuario_actual: dict[str, object]) -> int:
    roles = {str(rol) for rol in usuario_actual.get("roles", [])}
    if "CLIENTE" not in roles:
        raise HTTPException(status_code=403, detail="Solo clientes pueden pagar compras digitales.")
    cliente_id = repo.obtener_cliente_id_por_usuario(int(usuario_actual["id"]))
    if cliente_id is None:
        raise HTTPException(status_code=403, detail="El usuario no tiene cliente asociado.")
    return cliente_id


def _validar_acceso_orden(usuario_actual: dict[str, object], orden: dict) -> None:
    roles = {str(rol) for rol in usuario_actual.get("roles", [])}
    if "ADMINISTRADOR" in roles:
        return
    cliente_id = repo.obtener_cliente_id_por_usuario(int(usuario_actual["id"]))
    if cliente_id is None or int(orden["cliente_id"]) != cliente_id:
        raise HTTPException(status_code=404, detail="Orden de pago no encontrada.")


def _checkout_response(orden: dict) -> CheckoutStripeResponse:
    return CheckoutStripeResponse(
        orden_id=int(orden["id"]),
        venta_id=int(orden["venta_id"]),
        estado=str(orden["estado"]),
        checkout_url=str(orden["checkout_url"]),
    )


def _orden_response(orden: dict) -> OrdenPagoResponse:
    return OrdenPagoResponse(
        orden_id=int(orden["id"]),
        venta_id=int(orden["venta_id"]),
        cliente_id=int(orden["cliente_id"]) if orden.get("cliente_id") is not None else None,
        monto_total=orden["monto_total"],
        moneda=str(orden["moneda"]),
        metodo=str(orden["metodo"]),
        estado=str(orden["estado"]),
        proveedor=str(orden["proveedor"]),
        checkout_url=orden.get("checkout_url"),
        proveedor_session_id=orden.get("proveedor_session_id"),
        fecha_pago=orden["fecha_pago"].isoformat() if orden.get("fecha_pago") else None,
    )
