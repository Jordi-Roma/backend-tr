from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

TipoReporte = Literal[
    "VENTAS", "PRODUCTOS_MAS_VENDIDOS", "INVENTARIO", "RESERVAS", "MOVIMIENTOS", "TRANSFERENCIAS"
]


class ReporteRequest(BaseModel):
    tipo: TipoReporte
    fecha_desde: date
    fecha_hasta: date
    sucursal_id: int | None = Field(default=None, gt=0)
    agrupacion: Literal["DIA", "MES"] = "DIA"
    solo_bajo_stock: bool = False

    @model_validator(mode="after")
    def validar_rango(self):
        if self.fecha_desde > self.fecha_hasta:
            raise ValueError("La fecha inicial no puede ser posterior a la final.")
        if (self.fecha_hasta - self.fecha_desde).days > 366:
            raise ValueError("El periodo maximo permitido es de 366 dias.")
        return self


class InterpretarRequest(BaseModel):
    texto: str = Field(min_length=3, max_length=500)
