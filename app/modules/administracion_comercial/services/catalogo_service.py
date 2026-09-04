from fastapi import HTTPException

from app.modules.administracion_comercial.repositories.catalogo_repository import (
    activar_categoria,
    activar_color,
    activar_talla,
    actualizar_categoria,
    actualizar_color,
    actualizar_talla,
    contar_productos_activos_por_categoria,
    contar_variantes_activas_por_color,
    contar_variantes_activas_por_talla,
    crear_categoria,
    crear_color,
    crear_talla,
    desactivar_categoria,
    desactivar_color,
    desactivar_talla,
    listar_categorias,
    listar_colores,
    listar_tallas,
    obtener_categoria_por_id,
    obtener_categoria_por_nombre,
    obtener_color_por_id,
    obtener_color_por_nombre,
    obtener_talla_por_id,
    obtener_talla_por_nombre,
)
from app.modules.administracion_comercial.schemas.catalogo.catalogo_request import (
    ActualizarCategoriaRequest,
    ActualizarColorRequest,
    ActualizarTallaRequest,
    CrearCategoriaRequest,
    CrearColorRequest,
    CrearTallaRequest,
)
from app.modules.administracion_comercial.schemas.catalogo.catalogo_response import (
    CategoriaResponse,
    ColorResponse,
    MensajeResponse,
    TallaResponse,
)


# ═══════════════════════════════════════════════════════════════════════════
# CATEGORÍAS
# ═══════════════════════════════════════════════════════════════════════════

def obtener_categorias() -> list[CategoriaResponse]:
    categorias = listar_categorias()
    return [construir_categoria_response(c) for c in categorias]


def obtener_categoria(categoria_id: int) -> CategoriaResponse:
    categoria = obtener_categoria_por_id(categoria_id)

    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    return construir_categoria_response(categoria)


def registrar_categoria(
    request: CrearCategoriaRequest,
    usuario_actual: dict[str, object],
) -> CategoriaResponse:
    if obtener_categoria_por_nombre(request.nombre) is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una categoría con ese nombre.",
        )

    categoria = crear_categoria(
        nombre=request.nombre.strip(),
        descripcion=request.descripcion,
    )
    return construir_categoria_response(categoria)


def editar_categoria(
    categoria_id: int,
    request: ActualizarCategoriaRequest,
    usuario_actual: dict[str, object],
) -> CategoriaResponse:
    actual = obtener_categoria_por_id(categoria_id)

    if actual is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    existente = obtener_categoria_por_nombre(request.nombre)
    if existente is not None and int(existente["id"]) != categoria_id:
        raise HTTPException(
            status_code=409,
            detail="Ya existe otra categoría con ese nombre.",
        )

    categoria = actualizar_categoria(
        categoria_id=categoria_id,
        nombre=request.nombre.strip(),
        descripcion=request.descripcion,
    )

    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    return construir_categoria_response(categoria)


def eliminar_categoria(
    categoria_id: int,
    usuario_actual: dict[str, object],
) -> MensajeResponse:
    categoria = obtener_categoria_por_id(categoria_id)

    if categoria is None or categoria["activo"] is not True:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    total_productos = contar_productos_activos_por_categoria(categoria_id)

    if total_productos > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No se puede desactivar la categoría porque tiene "
                f"{total_productos} producto(s) activo(s) asociado(s)."
            ),
        )

    desactivado = desactivar_categoria(categoria_id)

    if not desactivado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    return MensajeResponse(mensaje="Categoría desactivada correctamente.")


def reactivar_categoria(
    categoria_id: int,
    usuario_actual: dict[str, object],
) -> CategoriaResponse:
    categoria_actual = obtener_categoria_por_id(categoria_id)

    if categoria_actual is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    categoria = activar_categoria(categoria_id)

    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    return construir_categoria_response(categoria)


def construir_categoria_response(categoria: dict[str, object]) -> CategoriaResponse:
    return CategoriaResponse(
        id=int(categoria["id"]),
        nombre=str(categoria["nombre"]),
        descripcion=str(categoria["descripcion"]) if categoria["descripcion"] is not None else None,
        activo=bool(categoria["activo"]),
        fecha_creacion=categoria["fecha_creacion"],
    )


# ═══════════════════════════════════════════════════════════════════════════
# TALLAS
# ═══════════════════════════════════════════════════════════════════════════

def obtener_tallas() -> list[TallaResponse]:
    tallas = listar_tallas()
    return [construir_talla_response(t) for t in tallas]


def obtener_talla(talla_id: int) -> TallaResponse:
    talla = obtener_talla_por_id(talla_id)

    if talla is None:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    return construir_talla_response(talla)


def registrar_talla(
    request: CrearTallaRequest,
    usuario_actual: dict[str, object],
) -> TallaResponse:
    if obtener_talla_por_nombre(request.nombre) is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una talla con ese nombre.",
        )

    talla = crear_talla(
        nombre=request.nombre.strip(),
        descripcion=request.descripcion,
    )
    return construir_talla_response(talla)


def editar_talla(
    talla_id: int,
    request: ActualizarTallaRequest,
    usuario_actual: dict[str, object],
) -> TallaResponse:
    actual = obtener_talla_por_id(talla_id)

    if actual is None:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    existente = obtener_talla_por_nombre(request.nombre)
    if existente is not None and int(existente["id"]) != talla_id:
        raise HTTPException(
            status_code=409,
            detail="Ya existe otra talla con ese nombre.",
        )

    talla = actualizar_talla(
        talla_id=talla_id,
        nombre=request.nombre.strip(),
        descripcion=request.descripcion,
    )

    if talla is None:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    return construir_talla_response(talla)


def eliminar_talla(
    talla_id: int,
    usuario_actual: dict[str, object],
) -> MensajeResponse:
    talla = obtener_talla_por_id(talla_id)

    if talla is None or talla["activo"] is not True:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    total_variantes = contar_variantes_activas_por_talla(talla_id)

    if total_variantes > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No se puede desactivar la talla porque tiene "
                f"{total_variantes} variante(s) activa(s) asociada(s)."
            ),
        )

    desactivado = desactivar_talla(talla_id)

    if not desactivado:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    return MensajeResponse(mensaje="Talla desactivada correctamente.")


def reactivar_talla(
    talla_id: int,
    usuario_actual: dict[str, object],
) -> TallaResponse:
    talla_actual = obtener_talla_por_id(talla_id)

    if talla_actual is None:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    talla = activar_talla(talla_id)

    if talla is None:
        raise HTTPException(status_code=404, detail="Talla no encontrada.")

    return construir_talla_response(talla)


def construir_talla_response(talla: dict[str, object]) -> TallaResponse:
    return TallaResponse(
        id=int(talla["id"]),
        nombre=str(talla["nombre"]),
        descripcion=str(talla["descripcion"]) if talla["descripcion"] is not None else None,
        activo=bool(talla["activo"]),
        fecha_creacion=talla["fecha_creacion"],
    )


# ═══════════════════════════════════════════════════════════════════════════
# COLORES
# ═══════════════════════════════════════════════════════════════════════════

def obtener_colores() -> list[ColorResponse]:
    colores = listar_colores()
    return [construir_color_response(c) for c in colores]


def obtener_color(color_id: int) -> ColorResponse:
    color = obtener_color_por_id(color_id)

    if color is None:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    return construir_color_response(color)


def registrar_color(
    request: CrearColorRequest,
    usuario_actual: dict[str, object],
) -> ColorResponse:
    if obtener_color_por_nombre(request.nombre) is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un color con ese nombre.",
        )

    color = crear_color(
        nombre=request.nombre.strip(),
        codigo_hex=request.codigo_hex,
    )
    return construir_color_response(color)


def editar_color(
    color_id: int,
    request: ActualizarColorRequest,
    usuario_actual: dict[str, object],
) -> ColorResponse:
    actual = obtener_color_por_id(color_id)

    if actual is None:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    existente = obtener_color_por_nombre(request.nombre)
    if existente is not None and int(existente["id"]) != color_id:
        raise HTTPException(
            status_code=409,
            detail="Ya existe otro color con ese nombre.",
        )

    color = actualizar_color(
        color_id=color_id,
        nombre=request.nombre.strip(),
        codigo_hex=request.codigo_hex,
    )

    if color is None:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    return construir_color_response(color)


def eliminar_color(
    color_id: int,
    usuario_actual: dict[str, object],
) -> MensajeResponse:
    color = obtener_color_por_id(color_id)

    if color is None or color["activo"] is not True:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    total_variantes = contar_variantes_activas_por_color(color_id)

    if total_variantes > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"No se puede desactivar el color porque tiene "
                f"{total_variantes} variante(s) activa(s) asociada(s)."
            ),
        )

    desactivado = desactivar_color(color_id)

    if not desactivado:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    return MensajeResponse(mensaje="Color desactivado correctamente.")


def reactivar_color(
    color_id: int,
    usuario_actual: dict[str, object],
) -> ColorResponse:
    color_actual = obtener_color_por_id(color_id)

    if color_actual is None:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    color = activar_color(color_id)

    if color is None:
        raise HTTPException(status_code=404, detail="Color no encontrado.")

    return construir_color_response(color)


def construir_color_response(color: dict[str, object]) -> ColorResponse:
    return ColorResponse(
        id=int(color["id"]),
        nombre=str(color["nombre"]),
        codigo_hex=str(color["codigo_hex"]) if color["codigo_hex"] is not None else None,
        activo=bool(color["activo"]),
        fecha_creacion=color["fecha_creacion"],
    )
