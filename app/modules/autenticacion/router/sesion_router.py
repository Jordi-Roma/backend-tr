from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.autenticacion.schemas.sesion.sesion_request import LoginRequest
from app.modules.autenticacion.schemas.sesion.sesion_response import (
    LoginResponse,
    LogoutResponse,
)
from app.modules.autenticacion.services.sesion_service import cerrar_sesion, iniciar_sesion

router = APIRouter(
    prefix="/api/v1/autenticacion",
    tags=["Autenticacion"],
)

bearer_scheme = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    return iniciar_sesion(request)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> LogoutResponse:
    token = credentials.credentials
    return cerrar_sesion(token)
