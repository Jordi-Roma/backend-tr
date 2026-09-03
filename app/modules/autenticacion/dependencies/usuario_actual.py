from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verificar_token_acceso
from app.modules.autenticacion.repositories.usuario_repository import (
    obtener_usuario_por_id,
)

bearer_scheme = HTTPBearer()


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, object]:
    token = credentials.credentials

    try:
        payload = verificar_token_acceso(token)
    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail="Token invalido o expirado.",
        ) from error

    usuario_id_token = payload.get("sub")

    try:
        usuario_id = int(str(usuario_id_token))
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=401,
            detail="Token invalido.",
        ) from error

    usuario = obtener_usuario_por_id(usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado.",
        )

    if usuario["activo"] is not True:
        raise HTTPException(
            status_code=403,
            detail="Usuario inactivo.",
        )

    return usuario
