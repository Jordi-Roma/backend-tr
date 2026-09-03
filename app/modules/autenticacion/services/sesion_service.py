from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.security import crear_token_acceso, verificar_password, verificar_token_acceso
from app.modules.autenticacion.repositories.sesion_repository import (
    cerrar_sesion_activa,
    crear_sesion,
    incrementar_intento_fallido,
    obtener_usuario_para_login,
    registrar_bitacora_login,
    reiniciar_intentos_login,
)
from app.modules.autenticacion.schemas.sesion.sesion_request import LoginRequest
from app.modules.autenticacion.schemas.sesion.sesion_response import (
    LoginResponse,
    LogoutResponse,
)


def iniciar_sesion(request: LoginRequest) -> LoginResponse:
    identificador = request.identificador.strip().lower()
    usuario = obtener_usuario_para_login(identificador)

    if usuario is None:
        registrar_bitacora_login(
            None,
            "INICIO_SESION_FALLIDO",
            "FALLIDO",
            "Intento de inicio de sesion con credenciales incorrectas.",
        )
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    usuario_id = int(usuario["id"])

    if not bool(usuario["activo"]):
        registrar_bitacora_login(
            usuario_id,
            "INICIO_SESION_FALLIDO",
            "FALLIDO",
            "Intento de inicio de sesion con usuario inactivo.",
        )
        raise HTTPException(status_code=403, detail="Usuario inactivo.")

    bloqueado_hasta = usuario["bloqueado_hasta"]

    if isinstance(bloqueado_hasta, datetime):
        bloqueado_hasta_utc = bloqueado_hasta

        if bloqueado_hasta_utc.tzinfo is None:
            bloqueado_hasta_utc = bloqueado_hasta_utc.replace(tzinfo=timezone.utc)

        if bloqueado_hasta_utc > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=403,
                detail=(
                    "Usuario bloqueado temporalmente. "
                    "Intente nuevamente en unos minutos."
                ),
            )

    password_correcto = verificar_password(
        request.password,
        str(usuario["password_hash"]),
    )

    if not password_correcto:
        intento = incrementar_intento_fallido(usuario_id)
        registrar_bitacora_login(
            usuario_id,
            "INICIO_SESION_FALLIDO",
            "FALLIDO",
            "Intento de inicio de sesion con contrasena incorrecta.",
        )

        if int(intento["intentos_fallidos"]) >= 5:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Usuario bloqueado por multiples intentos fallidos. "
                    "Intente nuevamente en 3 minutos."
                ),
            )

        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    roles = [str(rol) for rol in usuario["roles"]]

    reiniciar_intentos_login(usuario_id)
    access_token = crear_token_acceso(
        {
            "sub": str(usuario_id),
            "username": str(usuario["username"]),
            "correo": str(usuario["correo"]),
            "roles": roles,
        }
    )
    crear_sesion(usuario_id)
    registrar_bitacora_login(
        usuario_id,
        "INICIO_SESION_EXITOSO",
        "EXITOSO",
        "Inicio de sesion exitoso.",
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario_id=usuario_id,
        nombre=str(usuario["nombre"]),
        apellido=str(usuario["apellido"]),
        username=str(usuario["username"]),
        correo=str(usuario["correo"]),
        roles=roles,
        mensaje="Inicio de sesion exitoso.",
    )


def cerrar_sesion(token: str) -> LogoutResponse:
    try:
        payload = verificar_token_acceso(token)
    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail="Token invalido o expirado.",
        ) from error

    usuario_id_texto = payload.get("sub")

    if not isinstance(usuario_id_texto, str) or not usuario_id_texto.isdigit():
        raise HTTPException(status_code=401, detail="Token invalido.")

    usuario_id = int(usuario_id_texto)
    sesion_cerrada = cerrar_sesion_activa(usuario_id)

    if not sesion_cerrada:
        raise HTTPException(
            status_code=404,
            detail="No existe una sesion activa para cerrar.",
        )

    registrar_bitacora_login(
        usuario_id,
        "CIERRE_SESION",
        "EXITOSO",
        "Cierre de sesion exitoso.",
    )

    return LogoutResponse(mensaje="Sesion cerrada correctamente.")
