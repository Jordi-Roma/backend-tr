from fastapi import APIRouter, Depends

from app.modules.administracion_comercial.schemas.ciudad_sucursal.ciudad_sucursal_request import (
    ActualizarCiudadRequest,
    ActualizarSucursalRequest,
    CrearCiudadRequest,
    CrearSucursalRequest,
)
from app.modules.administracion_comercial.schemas.ciudad_sucursal.ciudad_sucursal_response import (
    CiudadResponse,
    MensajeResponse,
    SucursalResponse,
)
from app.modules.administracion_comercial.services.ciudad_sucursal_service import (
    editar_ciudad,
    editar_sucursal,
    eliminar_ciudad,
    eliminar_sucursal,
    obtener_ciudad,
    obtener_ciudades,
    obtener_sucursal,
    obtener_sucursales,
    reactivar_ciudad,
    reactivar_sucursal,
    registrar_ciudad,
    registrar_sucursal,
)
from app.modules.autenticacion.dependencies.admin_required import requerir_admin

router = APIRouter(
    prefix="/api/v1",
    tags=["Ciudades y Sucursales"],
)


@router.get("/ciudades", response_model=list[CiudadResponse])
def listar_ciudades_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[CiudadResponse]:
    return obtener_ciudades()


@router.post("/ciudades", response_model=CiudadResponse)
def crear_ciudad_endpoint(
    request: CrearCiudadRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CiudadResponse:
    return registrar_ciudad(request, usuario_actual)


@router.get("/ciudades/{ciudad_id}", response_model=CiudadResponse)
def obtener_ciudad_endpoint(
    ciudad_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CiudadResponse:
    return obtener_ciudad(ciudad_id)


@router.put("/ciudades/{ciudad_id}", response_model=CiudadResponse)
def actualizar_ciudad_endpoint(
    ciudad_id: int,
    request: ActualizarCiudadRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CiudadResponse:
    return editar_ciudad(ciudad_id, request, usuario_actual)


@router.patch("/ciudades/{ciudad_id}/desactivar", response_model=MensajeResponse)
def desactivar_ciudad_endpoint(
    ciudad_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_ciudad(ciudad_id, usuario_actual)


@router.patch("/ciudades/{ciudad_id}/activar", response_model=MensajeResponse)
def activar_ciudad_endpoint(
    ciudad_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return reactivar_ciudad(ciudad_id, usuario_actual)


@router.get("/sucursales", response_model=list[SucursalResponse])
def listar_sucursales_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[SucursalResponse]:
    return obtener_sucursales()


@router.post("/sucursales", response_model=SucursalResponse)
def crear_sucursal_endpoint(
    request: CrearSucursalRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> SucursalResponse:
    return registrar_sucursal(request, usuario_actual)


@router.get("/sucursales/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal_endpoint(
    sucursal_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> SucursalResponse:
    return obtener_sucursal(sucursal_id)


@router.put("/sucursales/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal_endpoint(
    sucursal_id: int,
    request: ActualizarSucursalRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> SucursalResponse:
    return editar_sucursal(sucursal_id, request, usuario_actual)


@router.patch("/sucursales/{sucursal_id}/desactivar", response_model=MensajeResponse)
def desactivar_sucursal_endpoint(
    sucursal_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_sucursal(sucursal_id, usuario_actual)


@router.patch("/sucursales/{sucursal_id}/activar", response_model=MensajeResponse)
def activar_sucursal_endpoint(
    sucursal_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return reactivar_sucursal(sucursal_id, usuario_actual)
