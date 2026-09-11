from pydantic import BaseModel


class CrearReservaDesdeCarritoRequest(BaseModel):
    sucursal_id: int
    observacion: str | None = None


class CambiarEstadoReservaRequest(BaseModel):
    estado: str
