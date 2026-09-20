from decimal import Decimal
from uuid import uuid4

from psycopg2.extras import RealDictCursor

from app.database.connection import get_connection
from app.modules.ventas_inventario.repositories.inventario_repository import _aplicar_movimiento


def obtener_cliente_id_por_usuario(usuario_id: int) -> int | None:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id
                FROM cliente
                WHERE usuario_id = %s AND activo = TRUE
                LIMIT 1;
                """,
                (usuario_id,),
            )
            row = cursor.fetchone()
            return int(row["id"]) if row else None
    finally:
        connection.close()


def crear_orden_desde_carrito(cliente_id: int, usuario_id: int, sucursal_id: int | None) -> dict:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            carrito_id = _obtener_carrito_activo(cursor, cliente_id)
            if carrito_id is None:
                raise ValueError("El carrito esta vacio.")

            items = _obtener_items_carrito(cursor, carrito_id, sucursal_id)
            if not items:
                raise ValueError("El carrito esta vacio.")

            for item in items:
                if item["sucursal_id"] is None:
                    raise ValueError("Selecciona una sucursal para todos los items del carrito.")
                if Decimal(item["precio_unitario"]) <= 0:
                    raise ValueError("Una prenda no tiene precio vigente.")
                if int(item["stock_disponible"]) < int(item["cantidad"]):
                    raise ValueError("No hay stock suficiente para completar la compra.")

            sucursales = {int(item["sucursal_id"]) for item in items}
            if len(sucursales) != 1:
                raise ValueError("La compra digital debe realizarse desde una sola sucursal.")

            subtotal_total = sum((Decimal(item["subtotal"]) for item in items), Decimal("0.00"))
            venta_id = _crear_venta_pendiente(cursor, usuario_id, cliente_id, next(iter(sucursales)), subtotal_total)
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO venta_detalle (
                        venta_id,
                        producto_variante_id,
                        cantidad,
                        precio_unitario,
                        descuento,
                        subtotal
                    )
                    VALUES (%s, %s, %s, %s, 0, %s);
                    """,
                    (
                        venta_id,
                        item["producto_variante_id"],
                        item["cantidad"],
                        item["precio_unitario"],
                        item["subtotal"],
                    ),
                )

            cursor.execute(
                """
                INSERT INTO orden_pago (
                    venta_id,
                    cliente_id,
                    monto_total,
                    moneda,
                    metodo,
                    estado,
                    proveedor
                )
                VALUES (%s, %s, %s, 'BOB', 'TARJETA', 'PENDIENTE', 'STRIPE')
                RETURNING *;
                """,
                (venta_id, cliente_id, subtotal_total),
            )
            orden = dict(cursor.fetchone())
            connection.commit()
            orden["items"] = items
            return orden
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def actualizar_checkout_stripe(orden_id: int, session_id: str, checkout_url: str, payment_intent_id: str | None) -> dict:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE orden_pago
                SET proveedor_session_id = %s,
                    proveedor_payment_intent_id = %s,
                    checkout_url = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *;
                """,
                (session_id, payment_intent_id, checkout_url, orden_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Orden de pago no encontrada.")
        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def obtener_orden_pago(orden_id: int) -> dict | None:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT *
                FROM orden_pago
                WHERE id = %s AND activo = TRUE
                LIMIT 1;
                """,
                (orden_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        connection.close()


def obtener_orden_por_session(session_id: str) -> dict | None:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT *
                FROM orden_pago
                WHERE proveedor_session_id = %s AND activo = TRUE
                LIMIT 1;
                """,
                (session_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        connection.close()


def marcar_orden_pagada(orden_id: int, usuario_id_movimiento: int | None = None) -> dict:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT op.*, v.sucursal_id, v.usuario_id
                FROM orden_pago op
                JOIN venta v ON v.id = op.venta_id
                WHERE op.id = %s AND op.activo = TRUE
                FOR UPDATE;
                """,
                (orden_id,),
            )
            orden = cursor.fetchone()
            if orden is None:
                raise ValueError("Orden de pago no encontrada.")
            orden = dict(orden)
            if orden["estado"] == "PAGADO":
                connection.commit()
                return _obtener_orden_cursor(cursor, orden_id)
            if orden["estado"] != "PENDIENTE":
                raise ValueError("La orden no esta pendiente.")

            cursor.execute(
                """
                SELECT producto_variante_id, cantidad
                FROM venta_detalle
                WHERE venta_id = %s
                ORDER BY id ASC;
                """,
                (orden["venta_id"],),
            )
            detalles = [dict(row) for row in cursor.fetchall()]
            usuario_movimiento = usuario_id_movimiento or orden["usuario_id"]
            for detalle in detalles:
                _aplicar_movimiento(
                    cursor,
                    usuario_movimiento,
                    int(orden["sucursal_id"]),
                    int(detalle["producto_variante_id"]),
                    "VENTA_DIGITAL",
                    int(detalle["cantidad"]),
                    "Pago digital confirmado por Stripe",
                    "VENTA",
                    int(orden["venta_id"]),
                )

            cursor.execute(
                """
                UPDATE venta
                SET estado = 'COMPLETADA',
                    metodo_pago = 'STRIPE'
                WHERE id = %s;
                """,
                (orden["venta_id"],),
            )
            cursor.execute(
                """
                UPDATE orden_pago
                SET estado = 'PAGADO',
                    fecha_pago = CURRENT_TIMESTAMP,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (orden_id,),
            )
            cursor.execute(
                """
                UPDATE carrito_item
                SET activo = FALSE,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE carrito_id IN (
                    SELECT id FROM carrito WHERE cliente_id = %s AND activo = TRUE
                );
                """,
                (orden["cliente_id"],),
            )
            resultado = _obtener_orden_cursor(cursor, orden_id)
        connection.commit()
        return resultado
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def marcar_orden_no_pagada(orden_id: int, estado_orden: str, estado_venta: str) -> dict:
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT venta_id, estado
                FROM orden_pago
                WHERE id = %s AND activo = TRUE
                FOR UPDATE;
                """,
                (orden_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Orden de pago no encontrada.")
            if row["estado"] == "PAGADO":
                return _obtener_orden_cursor(cursor, orden_id)
            cursor.execute(
                """
                UPDATE orden_pago
                SET estado = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (estado_orden, orden_id),
            )
            cursor.execute(
                """
                UPDATE venta
                SET estado = %s
                WHERE id = %s AND estado = 'PENDIENTE_PAGO';
                """,
                (estado_venta, row["venta_id"]),
            )
            resultado = _obtener_orden_cursor(cursor, orden_id)
        connection.commit()
        return resultado
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _obtener_carrito_activo(cursor, cliente_id: int) -> int | None:
    cursor.execute(
        """
        SELECT c.id
        FROM carrito c
        JOIN carrito_item ci ON ci.carrito_id = c.id AND ci.activo = TRUE
        WHERE c.cliente_id = %s AND c.activo = TRUE
        ORDER BY c.id DESC
        LIMIT 1;
        """,
        (cliente_id,),
    )
    row = cursor.fetchone()
    return int(row["id"]) if row else None


def _obtener_items_carrito(cursor, carrito_id: int, sucursal_id: int | None) -> list[dict]:
    cursor.execute(
        """
        SELECT
            ci.id,
            ci.producto_variante_id,
            p.nombre AS producto,
            ca.nombre AS categoria,
            t.nombre AS talla,
            co.nombre AS color,
            COALESCE(ci.sucursal_id, %s) AS sucursal_id,
            ci.cantidad,
            COALESCE(ci.precio_unitario, pp.precio, 0) AS precio_unitario,
            (COALESCE(ci.precio_unitario, pp.precio, 0) * ci.cantidad) AS subtotal,
            COALESCE(GREATEST(inv.stock_disponible - inv.stock_reservado, 0), 0)::INT AS stock_disponible
        FROM carrito_item ci
        JOIN producto_variante pv ON pv.id = ci.producto_variante_id AND pv.activo = TRUE
        JOIN producto p ON p.id = pv.producto_id AND p.activo = TRUE
        JOIN categoria ca ON ca.id = p.categoria_id
        JOIN talla t ON t.id = pv.talla_id
        JOIN color co ON co.id = pv.color_id
        LEFT JOIN precio_producto pp
            ON pp.producto_variante_id = pv.id
            AND pp.activo = TRUE
            AND CURRENT_DATE BETWEEN pp.fecha_inicio AND COALESCE(pp.fecha_fin, CURRENT_DATE)
        LEFT JOIN inventario_sucursal inv
            ON inv.producto_variante_id = pv.id
            AND inv.sucursal_id = COALESCE(ci.sucursal_id, %s)
            AND inv.activo = TRUE
        WHERE ci.carrito_id = %s AND ci.activo = TRUE
        ORDER BY ci.id ASC;
        """,
        (sucursal_id, sucursal_id, carrito_id),
    )
    return [dict(row) for row in cursor.fetchall()]


def _crear_venta_pendiente(cursor, usuario_id: int, cliente_id: int, sucursal_id: int, total: Decimal) -> int:
    codigo = f"WEB-{uuid4().hex[:10].upper()}"
    cursor.execute(
        """
        INSERT INTO venta (
            codigo,
            sucursal_id,
            usuario_id,
            cliente_id,
            tipo,
            estado,
            subtotal,
            descuento,
            total,
            metodo_pago,
            observacion
        )
        VALUES (%s, %s, %s, %s, 'WEB', 'PENDIENTE_PAGO', %s, 0, %s, 'STRIPE', 'Compra digital pendiente de pago')
        RETURNING id;
        """,
        (codigo, sucursal_id, usuario_id, cliente_id, total, total),
    )
    return int(cursor.fetchone()["id"])


def _obtener_orden_cursor(cursor, orden_id: int) -> dict:
    cursor.execute(
        """
        SELECT *
        FROM orden_pago
        WHERE id = %s
        LIMIT 1;
        """,
        (orden_id,),
    )
    return dict(cursor.fetchone())
