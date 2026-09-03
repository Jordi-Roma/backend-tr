from pydantic import BaseModel


class CiudadResponse(BaseModel):
    id: int
    nombre: str
    departamento: str | None
    activo: bool


class SucursalResponse(BaseModel):
    id: int
    ciudad_id: int
    ciudad_nombre: str
    nombre: str
    direccion: str
    telefono: str | None
    activo: bool


class MensajeResponse(BaseModel):
    mensaje: str
