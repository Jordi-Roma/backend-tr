from psycopg2.extras import RealDictCursor

from app.database.connection import get_connection


# ═══════════════════════════════════════════════════════════════════════════
# CATEGORÍAS
# ═══════════════════════════════════════════════════════════════════════════

def listar_categorias() -> list[dict[str, object]]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, descripcion, activo, fecha_creacion
            FROM categoria
            ORDER BY nombre ASC;
            """
        )
        return [dict(c) for c in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def obtener_categoria_por_id(categoria_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, descripcion, activo, fecha_creacion
            FROM categoria
            WHERE id = %s
            LIMIT 1;
            """,
            (categoria_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def obtener_categoria_por_nombre(nombre: str) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre
            FROM categoria
            WHERE lower(nombre) = lower(%s)
            LIMIT 1;
            """,
            (nombre,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def crear_categoria(
    nombre: str,
    descripcion: str | None,
) -> dict[str, object]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            INSERT INTO categoria (nombre, descripcion)
            VALUES (%s, %s)
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (nombre, descripcion),
        )
        row = cursor.fetchone()
        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def actualizar_categoria(
    categoria_id: int,
    nombre: str,
    descripcion: str | None,
) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE categoria
            SET nombre = %s,
                descripcion = %s
            WHERE id = %s
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (nombre, descripcion, categoria_id),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def desactivar_categoria(categoria_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE categoria
            SET activo = FALSE
            WHERE id = %s
                AND activo = TRUE
            RETURNING id;
            """,
            (categoria_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return False

        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def activar_categoria(categoria_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE categoria
            SET activo = TRUE
            WHERE id = %s
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (categoria_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def contar_productos_activos_por_categoria(categoria_id: int) -> int:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM producto
            WHERE categoria_id = %s
                AND activo = TRUE;
            """,
            (categoria_id,),
        )
        row = cursor.fetchone()
        return int(row["total"]) if row else 0
    finally:
        cursor.close()
        connection.close()


# ═══════════════════════════════════════════════════════════════════════════
# TALLAS
# ═══════════════════════════════════════════════════════════════════════════

def listar_tallas() -> list[dict[str, object]]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, descripcion, activo, fecha_creacion
            FROM talla
            ORDER BY nombre ASC;
            """
        )
        return [dict(t) for t in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def obtener_talla_por_id(talla_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, descripcion, activo, fecha_creacion
            FROM talla
            WHERE id = %s
            LIMIT 1;
            """,
            (talla_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def obtener_talla_por_nombre(nombre: str) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre
            FROM talla
            WHERE lower(nombre) = lower(%s)
            LIMIT 1;
            """,
            (nombre,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def crear_talla(
    nombre: str,
    descripcion: str | None,
) -> dict[str, object]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            INSERT INTO talla (nombre, descripcion)
            VALUES (%s, %s)
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (nombre, descripcion),
        )
        row = cursor.fetchone()
        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def actualizar_talla(
    talla_id: int,
    nombre: str,
    descripcion: str | None,
) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE talla
            SET nombre = %s,
                descripcion = %s
            WHERE id = %s
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (nombre, descripcion, talla_id),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def desactivar_talla(talla_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE talla
            SET activo = FALSE
            WHERE id = %s
                AND activo = TRUE
            RETURNING id;
            """,
            (talla_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return False

        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def activar_talla(talla_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE talla
            SET activo = TRUE
            WHERE id = %s
            RETURNING id, nombre, descripcion, activo, fecha_creacion;
            """,
            (talla_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def contar_variantes_activas_por_talla(talla_id: int) -> int:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM producto_variante
            WHERE talla_id = %s
                AND activo = TRUE;
            """,
            (talla_id,),
        )
        row = cursor.fetchone()
        return int(row["total"]) if row else 0
    finally:
        cursor.close()
        connection.close()


# ═══════════════════════════════════════════════════════════════════════════
# COLORES
# ═══════════════════════════════════════════════════════════════════════════

def listar_colores() -> list[dict[str, object]]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, codigo_hex, activo, fecha_creacion
            FROM color
            ORDER BY nombre ASC;
            """
        )
        return [dict(c) for c in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def obtener_color_por_id(color_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre, codigo_hex, activo, fecha_creacion
            FROM color
            WHERE id = %s
            LIMIT 1;
            """,
            (color_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def obtener_color_por_nombre(nombre: str) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT id, nombre
            FROM color
            WHERE lower(nombre) = lower(%s)
            LIMIT 1;
            """,
            (nombre,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        cursor.close()
        connection.close()


def crear_color(
    nombre: str,
    codigo_hex: str | None,
) -> dict[str, object]:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            INSERT INTO color (nombre, codigo_hex)
            VALUES (%s, %s)
            RETURNING id, nombre, codigo_hex, activo, fecha_creacion;
            """,
            (nombre, codigo_hex),
        )
        row = cursor.fetchone()
        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def actualizar_color(
    color_id: int,
    nombre: str,
    codigo_hex: str | None,
) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE color
            SET nombre = %s,
                codigo_hex = %s
            WHERE id = %s
            RETURNING id, nombre, codigo_hex, activo, fecha_creacion;
            """,
            (nombre, codigo_hex, color_id),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def desactivar_color(color_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE color
            SET activo = FALSE
            WHERE id = %s
                AND activo = TRUE
            RETURNING id;
            """,
            (color_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return False

        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def activar_color(color_id: int) -> dict[str, object] | None:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            UPDATE color
            SET activo = TRUE
            WHERE id = %s
            RETURNING id, nombre, codigo_hex, activo, fecha_creacion;
            """,
            (color_id,),
        )
        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()
        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def contar_variantes_activas_por_color(color_id: int) -> int:
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM producto_variante
            WHERE color_id = %s
                AND activo = TRUE;
            """,
            (color_id,),
        )
        row = cursor.fetchone()
        return int(row["total"]) if row else 0
    finally:
        cursor.close()
        connection.close()
