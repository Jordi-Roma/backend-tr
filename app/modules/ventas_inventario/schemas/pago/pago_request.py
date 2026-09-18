from pydantic import BaseModel, Field


class CrearCheckoutStripeRequest(BaseModel):
    sucursal_id: int | None = Field(default=None, gt=0)


class ConfirmarPagoPruebaRequest(BaseModel):
    aprobar: bool = True
