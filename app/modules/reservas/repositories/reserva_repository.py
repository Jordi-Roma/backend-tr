from decimal import Decimal
from uuid import uuid4

from psycopg2.extras import RealDictCursor

from app.database.connection import get_connection
from app.modules.reservas.repositories.carrito_repository import (
    _armar_carrito_cursor,
    _obtener_cliente_id_por_usuario_cursor,
    _obtener_o_crear_carrito_cursor,
)

ESTADOS_FINALES = {"COMPLETADA", "CANCELADA", "VENCIDA"}


def crear_reserva_desde_carrito(
    usuario_id: int,
    sucursal_id: int,
    observacion: str | None,
) -> dict[str, object]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cliente_id = _obtener_cliente_id_por_usuario_cursor(cursor, usuario_id)

        if cliente_id is None:
            raise ValueError("El usuario no tiene cliente asociado.")

        carrito_id = _obtener_o_crear_carrito_cursor(cursor, cliente_id)
        carrito = _armar_carrito_cursor(cursor, carrito_id)
        items = carrito["items"]

        if len(items) == 0:
            raise ValueError("El carrito esta vacio.")

        for item in items:
            variante_id = int(item["producto_variante_id"])
            cantidad = int(item["cantidad"])
            _validar_y_reservar_stock_cursor(cursor, variante_id, sucursal_id, cantidad)

        total = sum((item["subtotal"] or Decimal("0.00") for item in items), Decimal("0.00"))
        codigo = _generar_codigo_reserva()

        cursor.execute(
            """
            INSERT INTO reserva (
                cliente_id,
                sucursal_id,
                codigo,
                estado,
                total,
                fecha_expiracion,
                observacion
            )
            VALUES (
                %s,
                %s,
                %s,
                'PENDIENTE',
                %s,
                CURRENT_TIMESTAMP + INTERVAL '24 hours',
                %s
            )
            RETURNING id;
            """,
            (cliente_id, sucursal_id, codigo, total, observacion),
        )
        reserva_id = int(cursor.fetchone()["id"])

        for item in items:
            precio = item["precio_unitario"] or Decimal("0.00")
            cantidad = int(item["cantidad"])
            subtotal = precio * cantidad
            cursor.execute(
                """
                INSERT INTO reserva_detalle (
                    reserva_id,
                    producto_variante_id,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    reserva_id,
                    item["producto_variante_id"],
                    cantidad,
                    precio,
                    subtotal,
                ),
            )

        cursor.execute(
            """
            UPDATE carrito_item
            SET activo = FALSE,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE carrito_id = %s AND activo = TRUE;
            """,
            (carrito_id,),
        )

        _registrar_bitacora_cursor(
            cursor,
            usuario_id,
            "CREACION_RESERVA",
            f"Creacion de reserva {codigo}.",
        )

        connection.commit()
        reserva = _obtener_reserva_por_id_cursor(cursor, reserva_id)
        if reserva is None:
            raise RuntimeError("No se pudo recuperar la reserva creada.")
        return reserva
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def listar_reservas_cliente(usuario_id: int) -> list[dict[str, object]]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cliente_id = _obtener_cliente_id_por_usuario_cursor(cursor, usuario_id)

        if cliente_id is None:
            return []

        cursor.execute(
            """
            SELECT id
            FROM reserva
            WHERE cliente_id = %s AND activo = TRUE
            ORDER BY fecha_reserva DESC, id DESC;
            """,
            (cliente_id,),
        )
        return [
            reserva
            for reserva in (_obtener_reserva_por_id_cursor(cursor, int(row["id"])) for row in cursor.fetchall())
            if reserva is not None
        ]
    finally:
        cursor.close()
        connection.close()


def obtener_sucursal_empleado_usuario(usuario_id: int) -> int | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT sucursal_id
            FROM empleado
            WHERE usuario_id = %s AND activo = TRUE
            LIMIT 1;
            """,
            (usuario_id,),
        )
        row = cursor.fetchone()
        return int(row["sucursal_id"]) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def listar_reservas_admin(
    estado: str | None = None,
    sucursal_id: int | None = None,
) -> list[dict[str, object]]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        params: list[object] = []
        estado_sql = ""
        sucursal_sql = ""

        if estado:
            estado_sql = "AND estado = %s"
            params.append(estado)

        if sucursal_id is not None:
            sucursal_sql = "AND sucursal_id = %s"
            params.append(sucursal_id)

        cursor.execute(
            f"""
            SELECT id
            FROM reserva
            WHERE activo = TRUE {estado_sql} {sucursal_sql}
            ORDER BY fecha_reserva DESC, id DESC;
            """,
            params,
        )
        return [
            reserva
            for reserva in (_obtener_reserva_por_id_cursor(cursor, int(row["id"])) for row in cursor.fetchall())
            if reserva is not None
        ]
    finally:
        cursor.close()
        connection.close()


def obtener_reserva_cliente(usuario_id: int, reserva_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cliente_id = _obtener_cliente_id_por_usuario_cursor(cursor, usuario_id)

        if cliente_id is None:
            return None

        cursor.execute(
            """
            SELECT id
            FROM reserva
            WHERE id = %s AND cliente_id = %s AND activo = TRUE
            LIMIT 1;
            """,
            (reserva_id, cliente_id),
        )

        if cursor.fetchone() is None:
            return None

        return _obtener_reserva_por_id_cursor(cursor, reserva_id)
    finally:
        cursor.close()
        connection.close()


def obtener_reserva_admin(
    reserva_id: int,
    sucursal_id: int | None = None,
) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        reserva = _obtener_reserva_por_id_cursor(cursor, reserva_id)

        if reserva is None:
            return None

        if sucursal_id is not None and int(reserva["sucursal_id"]) != sucursal_id:
            return None

        return reserva
    finally:
        cursor.close()
        connection.close()


def cancelar_reserva_cliente(usuario_id: int, reserva_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cliente_id = _obtener_cliente_id_por_usuario_cursor(cursor, usuario_id)

        if cliente_id is None:
            connection.rollback()
            return None

        cursor.execute(
            """
            SELECT id, estado
            FROM reserva
            WHERE id = %s AND cliente_id = %s AND activo = TRUE
            FOR UPDATE;
            """,
            (reserva_id, cliente_id),
        )
        reserva = cursor.fetchone()

        if reserva is None:
            connection.rollback()
            return None

        if str(reserva["estado"]) in ESTADOS_FINALES:
            raise ValueError("La reserva ya esta en un estado final.")

        _liberar_stock_reserva_cursor(cursor, reserva_id)
        _actualizar_estado_reserva_cursor(cursor, reserva_id, "CANCELADA")
        _registrar_bitacora_cursor(
            cursor,
            usuario_id,
            "CANCELACION_RESERVA",
            f"Cancelacion de reserva {reserva_id}.",
        )

        connection.commit()
        return _obtener_reserva_por_id_cursor(cursor, reserva_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def cambiar_estado_reserva(
    usuario_id: int,
    reserva_id: int,
    nuevo_estado: str,
    sucursal_id: int | None = None,
) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, estado, sucursal_id
            FROM reserva
            WHERE id = %s AND activo = TRUE
            FOR UPDATE;
            """,
            (reserva_id,),
        )
        reserva = cursor.fetchone()

        if reserva is None:
            connection.rollback()
            return None

        if sucursal_id is not None and int(reserva["sucursal_id"]) != sucursal_id:
            connection.rollback()
            return None

        estado_actual = str(reserva["estado"])

        if estado_actual in ESTADOS_FINALES:
            raise ValueError("La reserva ya esta en un estado final.")

        if nuevo_estado in {"CANCELADA", "VENCIDA"}:
            _liberar_stock_reserva_cursor(cursor, reserva_id)

        _actualizar_estado_reserva_cursor(cursor, reserva_id, nuevo_estado)
        _registrar_bitacora_cursor(
            cursor,
            usuario_id,
            "CAMBIO_ESTADO_RESERVA",
            f"Cambio de estado de reserva {reserva_id}: {estado_actual} -> {nuevo_estado}.",
        )

        connection.commit()
        return _obtener_reserva_por_id_cursor(cursor, reserva_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def _validar_y_reservar_stock_cursor(
    cursor,
    producto_variante_id: int,
    sucursal_id: int,
    cantidad: int,
) -> None:
    cursor.execute(
        """
        SELECT id, stock_disponible, stock_reservado
        FROM inventario_sucursal
        WHERE producto_variante_id = %s
          AND sucursal_id = %s
          AND activo = TRUE
        FOR UPDATE;
        """,
        (producto_variante_id, sucursal_id),
    )
    inventario = cursor.fetchone()

    if inventario is None:
        raise ValueError("No existe inventario para una de las prendas en la sucursal seleccionada.")

    disponible = int(inventario["stock_disponible"]) - int(inventario["stock_reservado"])

    if disponible < cantidad:
        raise ValueError("No hay stock suficiente para confirmar la reserva.")

    cursor.execute(
        """
        UPDATE inventario_sucursal
        SET stock_reservado = stock_reservado + %s,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s;
        """,
        (cantidad, inventario["id"]),
    )


def _liberar_stock_reserva_cursor(cursor, reserva_id: int) -> None:
    cursor.execute(
        """
        SELECT r.sucursal_id, rd.producto_variante_id, rd.cantidad
        FROM reserva_detalle rd
        JOIN reserva r ON r.id = rd.reserva_id
        WHERE rd.reserva_id = %s AND rd.activo = TRUE;
        """,
        (reserva_id,),
    )
    detalles = cursor.fetchall()

    for detalle in detalles:
        cursor.execute(
            """
            UPDATE inventario_sucursal
            SET stock_reservado = GREATEST(stock_reservado - %s, 0),
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE sucursal_id = %s
              AND producto_variante_id = %s
              AND activo = TRUE;
            """,
            (
                detalle["cantidad"],
                detalle["sucursal_id"],
                detalle["producto_variante_id"],
            ),
        )


def _actualizar_estado_reserva_cursor(cursor, reserva_id: int, estado: str) -> None:
    cursor.execute(
        """
        UPDATE reserva
        SET estado = %s,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s;
        """,
        (estado, reserva_id),
    )


def _obtener_reserva_por_id_cursor(cursor, reserva_id: int) -> dict[str, object] | None:
    cursor.execute(
        """
        SELECT
            r.id,
            r.codigo,
            r.cliente_id,
            CONCAT(u.nombre, ' ', u.apellido) AS cliente,
            r.sucursal_id,
            s.nombre AS sucursal,
            ci.nombre AS ciudad,
            r.estado,
            r.total,
            r.fecha_reserva,
            r.fecha_expiracion,
            r.observacion
        FROM reserva r
        JOIN cliente cl ON cl.id = r.cliente_id
        JOIN usuario u ON u.id = cl.usuario_id
        JOIN sucursal s ON s.id = r.sucursal_id
        JOIN ciudad ci ON ci.id = s.ciudad_id
        WHERE r.id = %s AND r.activo = TRUE
        LIMIT 1;
        """,
        (reserva_id,),
    )
    reserva = cursor.fetchone()

    if reserva is None:
        return None

    cursor.execute(
        """
        SELECT
            rd.id,
            rd.producto_variante_id,
            p.id AS producto_id,
            p.nombre AS producto,
            ca.nombre AS categoria,
            t.nombre AS talla,
            co.nombre AS color,
            rd.cantidad,
            rd.precio_unitario,
            rd.subtotal
        FROM reserva_detalle rd
        JOIN producto_variante pv ON pv.id = rd.producto_variante_id
        JOIN producto p ON p.id = pv.producto_id
        JOIN categoria ca ON ca.id = p.categoria_id
        JOIN talla t ON t.id = pv.talla_id
        JOIN color co ON co.id = pv.color_id
        WHERE rd.reserva_id = %s AND rd.activo = TRUE
        ORDER BY rd.id ASC;
        """,
        (reserva_id,),
    )

    data = dict(reserva)
    data["detalles"] = [dict(row) for row in cursor.fetchall()]
    return data


def _registrar_bitacora_cursor(cursor, usuario_id: int, accion: str, descripcion: str) -> None:
    cursor.execute(
        """
        INSERT INTO bitacora (usuario_id, accion, modulo, descripcion, resultado)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (usuario_id, accion, "RESERVAS", descripcion, "EXITOSO"),
    )


def _generar_codigo_reserva() -> str:
    return f"RSV-{uuid4().hex[:10].upper()}"
