from datetime import datetime

from pydantic import BaseModel


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool
    fecha_creacion: datetime


class TallaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool
    fecha_creacion: datetime


class ColorResponse(BaseModel):
    id: int
    nombre: str
    codigo_hex: str | None
    activo: bool
    fecha_creacion: datetime


class MensajeResponse(BaseModel):
    mensaje: str
