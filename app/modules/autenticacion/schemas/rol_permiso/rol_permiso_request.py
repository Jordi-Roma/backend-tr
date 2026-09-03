from pydantic import BaseModel, field_validator


class CrearRolRequest(BaseModel):
    nombre: str
    descripcion: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip().upper()

        if not nombre:
            raise ValueError("El nombre del rol es obligatorio.")

        return nombre

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        descripcion = valor.strip()
        return descripcion or None


class ActualizarRolRequest(BaseModel):
    nombre: str
    descripcion: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip().upper()

        if not nombre:
            raise ValueError("El nombre del rol es obligatorio.")

        return nombre

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        descripcion = valor.strip()
        return descripcion or None


class CrearPermisoRequest(BaseModel):
    nombre: str
    modulo: str
    accion: str
    descripcion: str | None = None

    @field_validator("nombre", "modulo", "accion")
    @classmethod
    def validar_texto_obligatorio(cls, valor: str) -> str:
        texto = valor.strip().upper()

        if not texto:
            raise ValueError("Este campo es obligatorio.")

        return texto

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        descripcion = valor.strip()
        return descripcion or None
