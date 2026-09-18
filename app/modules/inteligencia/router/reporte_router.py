from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.modules.autenticacion.dependencies.admin_required import requerir_admin
from app.modules.inteligencia.exports.reporte_excel import crear_excel
from app.modules.inteligencia.exports.reporte_pdf import crear_pdf
from app.modules.inteligencia.schemas.reportes.reporte_request import InterpretarRequest, ReporteRequest
from app.modules.inteligencia.services.reporte_service import catalogo_reportes, generar_reporte, interpretar

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


@router.get("/catalogo")
def catalogo_endpoint(usuario_actual: dict[str, object] = Depends(requerir_admin)):
    return catalogo_reportes()


@router.post("/interpretar")
def interpretar_endpoint(request: InterpretarRequest, usuario_actual: dict[str, object] = Depends(requerir_admin)):
    return interpretar(request.texto)


@router.post("/generar")
def generar_endpoint(request: ReporteRequest, usuario_actual: dict[str, object] = Depends(requerir_admin)):
    return generar_reporte(request)


def _archivo(request: ReporteRequest, extension: str):
    reporte = generar_reporte(request)
    data = crear_pdf(reporte) if extension == "pdf" else crear_excel(reporte)
    mime = "application/pdf" if extension == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"{request.tipo.lower()}_{request.fecha_desde}_{request.fecha_hasta}.{extension}"
    return StreamingResponse(BytesIO(data), media_type=mime, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.post("/exportar/pdf")
def pdf_endpoint(request: ReporteRequest, usuario_actual: dict[str, object] = Depends(requerir_admin)):
    return _archivo(request, "pdf")


@router.post("/exportar/excel")
def excel_endpoint(request: ReporteRequest, usuario_actual: dict[str, object] = Depends(requerir_admin)):
    return _archivo(request, "xlsx")
