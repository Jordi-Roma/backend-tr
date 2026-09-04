from fastapi import HTTPException

from app.modules.administracion_comercial.repositories.proveedor_repository import (
    activar_proveedor,
    actualizar_proveedor,
    crear_proveedor,
    desactivar_proveedor,
    listar_proveedores,
    obtener_proveedor_por_id,
    obtener_proveedor_por_nit,
)
from app.modules.administracion_comercial.schemas.proveedor.proveedor_request import (
    ActualizarProveedorRequest,
    CrearProveedorRequest,
)
from app.modules.administracion_comercial.schemas.proveedor.proveedor_response import (
    MensajeResponse,
    ProveedorResponse,
)


def obtener_proveedores() -> list[ProveedorResponse]:
    proveedores = listar_proveedores()
    return [construir_proveedor_response(p) for p in proveedores]


def obtener_proveedor(proveedor_id: int) -> ProveedorResponse:
    proveedor = obtener_proveedor_por_id(proveedor_id)

    if proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    return construir_proveedor_response(proveedor)


def registrar_proveedor(
    request: CrearProveedorRequest,
    usuario_actual: dict[str, object],
) -> ProveedorResponse:
    if request.nit is not None:
        if obtener_proveedor_por_nit(request.nit) is not None:
            raise HTTPException(
                status_code=409,
                detail="El NIT ya esta registrado para otro proveedor.",
            )

    try:
        proveedor = crear_proveedor(
            nombre=request.nombre.strip(),
            nit=request.nit,
            telefono=request.telefono,
            correo=request.correo,
            direccion=request.direccion,
        )
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el proveedor.",
        ) from error

    return construir_proveedor_response(proveedor)


def editar_proveedor(
    proveedor_id: int,
    request: ActualizarProveedorRequest,
    usuario_actual: dict[str, object],
) -> ProveedorResponse:
    proveedor_actual = obtener_proveedor_por_id(proveedor_id)

    if proveedor_actual is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    try:
        proveedor = actualizar_proveedor(
            proveedor_id=proveedor_id,
            nombre=request.nombre.strip(),
            telefono=request.telefono,
            correo=request.correo,
            direccion=request.direccion,
        )
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar el proveedor.",
        ) from error

    if proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    return construir_proveedor_response(proveedor)


def eliminar_proveedor(
    proveedor_id: int,
    usuario_actual: dict[str, object],
) -> MensajeResponse:
    proveedor = obtener_proveedor_por_id(proveedor_id)

    if proveedor is None or proveedor["activo"] is not True:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    desactivado = desactivar_proveedor(proveedor_id)

    if not desactivado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    return MensajeResponse(mensaje="Proveedor desactivado correctamente.")


def reactivar_proveedor(
    proveedor_id: int,
    usuario_actual: dict[str, object],
) -> ProveedorResponse:
    proveedor_actual = obtener_proveedor_por_id(proveedor_id)

    if proveedor_actual is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    proveedor = activar_proveedor(proveedor_id)

    if proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    return construir_proveedor_response(proveedor)


def construir_proveedor_response(proveedor: dict[str, object]) -> ProveedorResponse:
    return ProveedorResponse(
        id=int(proveedor["id"]),
        nombre=str(proveedor["nombre"]),
        nit=str(proveedor["nit"]) if proveedor["nit"] is not None else None,
        telefono=str(proveedor["telefono"]) if proveedor["telefono"] is not None else None,
        correo=str(proveedor["correo"]) if proveedor["correo"] is not None else None,
        direccion=str(proveedor["direccion"]) if proveedor["direccion"] is not None else None,
        activo=bool(proveedor["activo"]),
        fecha_creacion=proveedor["fecha_creacion"],
    )
