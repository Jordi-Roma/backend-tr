from pydantic import BaseModel, field_validator


class CrearCiudadRequest(BaseModel):
    nombre: str
    departamento: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre de la ciudad es obligatorio.")

        return nombre

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        departamento = valor.strip()
        return departamento or None


class ActualizarCiudadRequest(BaseModel):
    nombre: str
    departamento: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre de la ciudad es obligatorio.")

        return nombre

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        departamento = valor.strip()
        return departamento or None


class CrearSucursalRequest(BaseModel):
    ciudad_id: int
    nombre: str
    direccion: str
    telefono: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre de la sucursal es obligatorio.")

        return nombre

    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor: str) -> str:
        direccion = valor.strip()

        if not direccion:
            raise ValueError("La direccion de la sucursal es obligatoria.")

        return direccion

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        telefono = valor.strip()
        return telefono or None


class ActualizarSucursalRequest(BaseModel):
    ciudad_id: int
    nombre: str
    direccion: str
    telefono: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        nombre = valor.strip()

        if not nombre:
            raise ValueError("El nombre de la sucursal es obligatorio.")

        return nombre

    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor: str) -> str:
        direccion = valor.strip()

        if not direccion:
            raise ValueError("La direccion de la sucursal es obligatoria.")

        return direccion

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str | None) -> str | None:
        if valor is None:
            return None

        telefono = valor.strip()
        return telefono or None
