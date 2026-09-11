from fastapi import HTTPException, status

from app.modules.reservas.repositories.reserva_repository import (
    cancelar_reserva_cliente,
    cambiar_estado_reserva,
    crear_reserva_desde_carrito,
    listar_reservas_admin,
    listar_reservas_cliente,
    obtener_reserva_admin,
    obtener_reserva_cliente,
    obtener_sucursal_empleado_usuario,
)
from app.modules.reservas.schemas.reserva_request import (
    CambiarEstadoReservaRequest,
    CrearReservaDesdeCarritoRequest,
)
from app.modules.reservas.schemas.reserva_response import ReservaResponse

ESTADOS_RESERVA = {"PENDIENTE", "PREPARADA", "EN_ATENCION", "COMPLETADA", "CANCELADA", "VENCIDA"}


def crear_desde_carrito(
    usuario_actual: dict[str, object],
    request: CrearReservaDesdeCarritoRequest,
) -> ReservaResponse:
    try:
        reserva = crear_reserva_desde_carrito(
            int(usuario_actual["id"]),
            request.sucursal_id,
            request.observacion,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return ReservaResponse(**reserva)


def listar_mis_reservas(usuario_actual: dict[str, object]) -> list[ReservaResponse]:
    return [ReservaResponse(**reserva) for reserva in listar_reservas_cliente(int(usuario_actual["id"]))]


def listar_todas(
    usuario_actual: dict[str, object],
    estado: str | None = None,
    sucursal_id: int | None = None,
) -> list[ReservaResponse]:
    if estado is not None:
        estado = estado.upper()
        _validar_estado(estado)

    sucursal_filtrada = _obtener_sucursal_permitida(usuario_actual, sucursal_id)
    return [ReservaResponse(**reserva) for reserva in listar_reservas_admin(estado, sucursal_filtrada)]


def obtener_mi_reserva(usuario_actual: dict[str, object], reserva_id: int) -> ReservaResponse:
    reserva = obtener_reserva_cliente(int(usuario_actual["id"]), reserva_id)

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return ReservaResponse(**reserva)


def obtener_reserva(usuario_actual: dict[str, object], reserva_id: int) -> ReservaResponse:
    sucursal_id = _obtener_sucursal_permitida(usuario_actual, None)
    reserva = obtener_reserva_admin(reserva_id, sucursal_id)

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return ReservaResponse(**reserva)


def cancelar_mi_reserva(usuario_actual: dict[str, object], reserva_id: int) -> ReservaResponse:
    try:
        reserva = cancelar_reserva_cliente(int(usuario_actual["id"]), reserva_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return ReservaResponse(**reserva)


def cambiar_estado(
    usuario_actual: dict[str, object],
    reserva_id: int,
    request: CambiarEstadoReservaRequest,
) -> ReservaResponse:
    estado = request.estado.upper()
    _validar_estado(estado)
    sucursal_id = _obtener_sucursal_permitida(usuario_actual, None)

    try:
        reserva = cambiar_estado_reserva(int(usuario_actual["id"]), reserva_id, estado, sucursal_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return ReservaResponse(**reserva)


def _validar_estado(estado: str) -> None:
    if estado not in ESTADOS_RESERVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado de reserva invalido.",
        )


def _obtener_sucursal_permitida(
    usuario_actual: dict[str, object],
    sucursal_id_solicitada: int | None,
) -> int | None:
    roles = [str(rol) for rol in usuario_actual.get("roles", [])]

    if "ADMINISTRADOR" in roles:
        return sucursal_id_solicitada

    if "ENCARGADO_SUCURSAL" in roles:
        sucursal_id = obtener_sucursal_empleado_usuario(int(usuario_actual["id"]))

        if sucursal_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El encargado no tiene sucursal asignada.",
            )

        return sucursal_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tiene permisos para gestionar reservas.",
    )
