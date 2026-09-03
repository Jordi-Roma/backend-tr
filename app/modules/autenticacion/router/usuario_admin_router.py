from fastapi import APIRouter, Depends

from app.modules.autenticacion.dependencies.admin_required import requerir_admin
from app.modules.autenticacion.schemas.usuario_admin.usuario_admin_request import (
    ActualizarUsuarioRequest,
)
from app.modules.autenticacion.schemas.usuario_admin.usuario_admin_response import (
    MensajeResponse,
    UsuarioAdminResponse,
)
from app.modules.autenticacion.services.usuario_admin_service import (
    activar_rol_usuario,
    asignar_rol_usuario,
    desactivar_rol_usuario,
    editar_usuario,
    eliminar_usuario,
    obtener_usuario,
    obtener_usuarios,
    reactivar_usuario,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Usuarios"],
)


@router.get("/usuarios", response_model=list[UsuarioAdminResponse])
def listar_usuarios_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[UsuarioAdminResponse]:
    return obtener_usuarios()


@router.get("/usuarios/{usuario_id}", response_model=UsuarioAdminResponse)
def obtener_usuario_endpoint(
    usuario_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> UsuarioAdminResponse:
    return obtener_usuario(usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioAdminResponse)
def actualizar_usuario_endpoint(
    usuario_id: int,
    request: ActualizarUsuarioRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> UsuarioAdminResponse:
    return editar_usuario(usuario_id, request, usuario_actual)


@router.patch("/usuarios/{usuario_id}/desactivar", response_model=MensajeResponse)
def desactivar_usuario_endpoint(
    usuario_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_usuario(usuario_id, usuario_actual)


@router.patch("/usuarios/{usuario_id}/activar", response_model=MensajeResponse)
def activar_usuario_endpoint(
    usuario_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return reactivar_usuario(usuario_id, usuario_actual)


@router.post("/usuarios/{usuario_id}/roles/{rol_id}", response_model=MensajeResponse)
def asignar_rol_endpoint(
    usuario_id: int,
    rol_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return asignar_rol_usuario(usuario_id, rol_id, usuario_actual)


@router.patch(
    "/usuarios/{usuario_id}/roles/{rol_id}/desactivar",
    response_model=MensajeResponse,
)
def desactivar_rol_endpoint(
    usuario_id: int,
    rol_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return desactivar_rol_usuario(usuario_id, rol_id, usuario_actual)


@router.patch(
    "/usuarios/{usuario_id}/roles/{rol_id}/activar",
    response_model=MensajeResponse,
)
def activar_rol_endpoint(
    usuario_id: int,
    rol_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return activar_rol_usuario(usuario_id, rol_id, usuario_actual)
