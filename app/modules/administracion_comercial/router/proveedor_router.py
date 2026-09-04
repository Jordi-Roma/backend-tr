from fastapi import APIRouter, Depends

from app.modules.administracion_comercial.schemas.proveedor.proveedor_request import (
    ActualizarProveedorRequest,
    CrearProveedorRequest,
)
from app.modules.administracion_comercial.schemas.proveedor.proveedor_response import (
    MensajeResponse,
    ProveedorResponse,
)
from app.modules.administracion_comercial.services.proveedor_service import (
    editar_proveedor,
    eliminar_proveedor,
    obtener_proveedor,
    obtener_proveedores,
    reactivar_proveedor,
    registrar_proveedor,
)
from app.modules.autenticacion.dependencies.admin_required import requerir_admin

router = APIRouter(
    prefix="/api/v1",
    tags=["Proveedores"],
)


@router.get("/proveedores", response_model=list[ProveedorResponse])
def listar_proveedores_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[ProveedorResponse]:
    return obtener_proveedores()


@router.post("/proveedores", response_model=ProveedorResponse)
def crear_proveedor_endpoint(
    request: CrearProveedorRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ProveedorResponse:
    return registrar_proveedor(request, usuario_actual)


@router.get("/proveedores/{proveedor_id}", response_model=ProveedorResponse)
def obtener_proveedor_endpoint(
    proveedor_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ProveedorResponse:
    return obtener_proveedor(proveedor_id)


@router.put("/proveedores/{proveedor_id}", response_model=ProveedorResponse)
def actualizar_proveedor_endpoint(
    proveedor_id: int,
    request: ActualizarProveedorRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ProveedorResponse:
    return editar_proveedor(proveedor_id, request, usuario_actual)


@router.patch("/proveedores/{proveedor_id}/desactivar", response_model=MensajeResponse)
def desactivar_proveedor_endpoint(
    proveedor_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_proveedor(proveedor_id, usuario_actual)


@router.patch("/proveedores/{proveedor_id}/activar", response_model=ProveedorResponse)
def activar_proveedor_endpoint(
    proveedor_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ProveedorResponse:
    return reactivar_proveedor(proveedor_id, usuario_actual)
