from fastapi import APIRouter

from app.modules.autenticacion.schemas.usuario.usuario_request import (
    UsuarioRegistroRequest,
)
from app.modules.autenticacion.schemas.usuario.usuario_response import (
    UsuarioRegistroResponse,
)
from app.modules.autenticacion.services.registro_service import registrar_cliente

router = APIRouter(
    prefix="/api/v1/autenticacion",
    tags=["Autenticacion"],
)


@router.post("/registro", response_model=UsuarioRegistroResponse)
def registrar_usuario(request: UsuarioRegistroRequest) -> UsuarioRegistroResponse:
    return registrar_cliente(request)
