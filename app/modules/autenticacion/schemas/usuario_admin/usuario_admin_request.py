import re

from pydantic import BaseModel, field_validator


class ActualizarUsuarioRequest(BaseModel):
    nombre: str
    apellido: str
    username: str
    correo: str

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_texto_obligatorio(cls, valor: str) -> str:
        texto = valor.strip()

        if not texto:
            raise ValueError("Este campo es obligatorio.")

        return texto

    @field_validator("username")
    @classmethod
    def validar_username(cls, valor: str) -> str:
        username = valor.strip().lower()

        if not username:
            raise ValueError("El username es obligatorio.")

        if len(username) < 4:
            raise ValueError("El username debe tener al menos 4 caracteres.")

        if " " in username:
            raise ValueError("El username no debe contener espacios.")

        if re.fullmatch(r"[a-z0-9_.]+", username) is None:
            raise ValueError(
                "El username solo puede tener letras, numeros, guion bajo y punto."
            )

        return username

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        correo = valor.strip().lower()

        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValueError("El correo no tiene un formato valido.")

        return correo
