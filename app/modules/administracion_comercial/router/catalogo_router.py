from fastapi import APIRouter, Depends

from app.modules.administracion_comercial.schemas.catalogo.catalogo_request import (
    ActualizarCategoriaRequest,
    ActualizarColorRequest,
    ActualizarTallaRequest,
    CrearCategoriaRequest,
    CrearColorRequest,
    CrearTallaRequest,
)
from app.modules.administracion_comercial.schemas.catalogo.catalogo_response import (
    CategoriaResponse,
    ColorResponse,
    MensajeResponse,
    TallaResponse,
)
from app.modules.administracion_comercial.services.catalogo_service import (
    editar_categoria,
    editar_color,
    editar_talla,
    eliminar_categoria,
    eliminar_color,
    eliminar_talla,
    obtener_categoria,
    obtener_categorias,
    obtener_color,
    obtener_colores,
    obtener_talla,
    obtener_tallas,
    reactivar_categoria,
    reactivar_color,
    reactivar_talla,
    registrar_categoria,
    registrar_color,
    registrar_talla,
)
from app.modules.autenticacion.dependencies.admin_required import requerir_admin

router = APIRouter(
    prefix="/api/v1",
    tags=["Catálogo"],
)


# ── CATEGORÍAS ─────────────────────────────────────────────────────────────

@router.get("/categorias", response_model=list[CategoriaResponse])
def listar_categorias_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[CategoriaResponse]:
    return obtener_categorias()


@router.post("/categorias", response_model=CategoriaResponse)
def crear_categoria_endpoint(
    request: CrearCategoriaRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CategoriaResponse:
    return registrar_categoria(request, usuario_actual)


@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria_endpoint(
    categoria_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CategoriaResponse:
    return obtener_categoria(categoria_id)


@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria_endpoint(
    categoria_id: int,
    request: ActualizarCategoriaRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CategoriaResponse:
    return editar_categoria(categoria_id, request, usuario_actual)


@router.patch("/categorias/{categoria_id}/desactivar", response_model=MensajeResponse)
def desactivar_categoria_endpoint(
    categoria_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_categoria(categoria_id, usuario_actual)


@router.patch("/categorias/{categoria_id}/activar", response_model=CategoriaResponse)
def activar_categoria_endpoint(
    categoria_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> CategoriaResponse:
    return reactivar_categoria(categoria_id, usuario_actual)


# ── TALLAS ─────────────────────────────────────────────────────────────────

@router.get("/tallas", response_model=list[TallaResponse])
def listar_tallas_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[TallaResponse]:
    return obtener_tallas()


@router.post("/tallas", response_model=TallaResponse)
def crear_talla_endpoint(
    request: CrearTallaRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> TallaResponse:
    return registrar_talla(request, usuario_actual)


@router.get("/tallas/{talla_id}", response_model=TallaResponse)
def obtener_talla_endpoint(
    talla_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> TallaResponse:
    return obtener_talla(talla_id)


@router.put("/tallas/{talla_id}", response_model=TallaResponse)
def actualizar_talla_endpoint(
    talla_id: int,
    request: ActualizarTallaRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> TallaResponse:
    return editar_talla(talla_id, request, usuario_actual)


@router.patch("/tallas/{talla_id}/desactivar", response_model=MensajeResponse)
def desactivar_talla_endpoint(
    talla_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_talla(talla_id, usuario_actual)


@router.patch("/tallas/{talla_id}/activar", response_model=TallaResponse)
def activar_talla_endpoint(
    talla_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> TallaResponse:
    return reactivar_talla(talla_id, usuario_actual)


# ── COLORES ────────────────────────────────────────────────────────────────

@router.get("/colores", response_model=list[ColorResponse])
def listar_colores_endpoint(
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> list[ColorResponse]:
    return obtener_colores()


@router.post("/colores", response_model=ColorResponse)
def crear_color_endpoint(
    request: CrearColorRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ColorResponse:
    return registrar_color(request, usuario_actual)


@router.get("/colores/{color_id}", response_model=ColorResponse)
def obtener_color_endpoint(
    color_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ColorResponse:
    return obtener_color(color_id)


@router.put("/colores/{color_id}", response_model=ColorResponse)
def actualizar_color_endpoint(
    color_id: int,
    request: ActualizarColorRequest,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ColorResponse:
    return editar_color(color_id, request, usuario_actual)


@router.patch("/colores/{color_id}/desactivar", response_model=MensajeResponse)
def desactivar_color_endpoint(
    color_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> MensajeResponse:
    return eliminar_color(color_id, usuario_actual)


@router.patch("/colores/{color_id}/activar", response_model=ColorResponse)
def activar_color_endpoint(
    color_id: int,
    usuario_actual: dict[str, object] = Depends(requerir_admin),
) -> ColorResponse:
    return reactivar_color(color_id, usuario_actual)
