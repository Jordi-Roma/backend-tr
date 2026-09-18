import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.modules.inteligencia.repositories.reporte_repository import consultar_reporte, listar_sucursales
from app.modules.inteligencia.schemas.reportes.reporte_request import ReporteRequest

TITULOS = {
    "VENTAS": "Ventas presenciales",
    "PRODUCTOS_MAS_VENDIDOS": "Productos más vendidos",
    "INVENTARIO": "Inventario por sucursal",
    "RESERVAS": "Reservas",
    "MOVIMIENTOS": "Movimientos de inventario",
    "TRANSFERENCIAS": "Transferencias de stock",
}
MONETARIOS = {"subtotal", "descuento", "total", "importe"}


def catalogo_reportes() -> dict[str, object]:
    return {"tipos": [{"id": key, "nombre": title} for key, title in TITULOS.items()], "sucursales": listar_sucursales()}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def interpretar(texto: str) -> dict[str, object]:
    normal = _normalizar(texto)
    hoy = datetime.now(ZoneInfo("America/La_Paz")).date()
    inicio, fin = hoy.replace(day=1), hoy
    if "semana pasada" in normal:
        fin = hoy - timedelta(days=hoy.weekday() + 1)
        inicio = fin - timedelta(days=6)
    elif "esta semana" in normal:
        inicio = hoy - timedelta(days=hoy.weekday())
    elif "este ano" in normal:
        inicio = hoy.replace(month=1, day=1)
    elif "mes pasado" in normal:
        fin = hoy.replace(day=1) - timedelta(days=1)
        inicio = fin.replace(day=1)
    elif "hoy" in normal:
        inicio = fin = hoy
    fechas = re.findall(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", normal)
    if len(fechas) == 2:
        try:
            inicio, fin = (date(int(a[2]), int(a[1]), int(a[0])) for a in fechas)
        except ValueError:
            return {"interpretado": False, "advertencias": ["Las fechas dictadas no son válidas."], "filtros": None}
    meses = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    rango_texto = re.search(r"\bdel?\s+(\d{1,2})\s+al\s+(\d{1,2})\s+de\s+(\w+)(?:\s+de\s+(\d{4}))?", normal)
    if rango_texto and rango_texto.group(3) in meses:
        try:
            ano = int(rango_texto.group(4) or hoy.year)
            mes = meses[rango_texto.group(3)]
            inicio = date(ano, mes, int(rango_texto.group(1)))
            fin = date(ano, mes, int(rango_texto.group(2)))
        except ValueError:
            return {"interpretado": False, "advertencias": ["El rango dictado no es válido."], "filtros": None}
    palabras = [
        ("PRODUCTOS_MAS_VENDIDOS", ("mas vendido", "mejor vendido", "top producto")),
        ("VENTAS", ("venta", "ventas", "ingreso", "ingresos")),
        ("INVENTARIO", ("inventario", "inventarios", "bajo stock", "existencia", "existencias")),
        ("RESERVAS", ("reserva", "reservas")),
        ("MOVIMIENTOS", ("movimiento", "movimientos", "entrada", "entradas", "salida", "salidas", "ajuste", "ajustes")),
        ("TRANSFERENCIAS", ("transferencia", "transferencias", "traslado", "traslados")),
    ]
    tipo = next((key for key, opciones in palabras if any(re.search(r"\b" + re.escape(p) + r"\b", normal) for p in opciones)), None)
    if not tipo:
        return {"interpretado": False, "advertencias": ["No se reconoció un tipo de reporte. Prueba con ventas, inventario, reservas, movimientos o transferencias."], "filtros": None}
    sucursal_id = None
    sucursales = listar_sucursales()
    for sucursal in sucursales:
        nombre = _normalizar(str(sucursal["nombre"]))
        if nombre in normal:
            sucursal_id = sucursal["id"]
            break
    if "sucursal" in normal and sucursal_id is None and "todas" not in normal:
        return {"interpretado": False, "advertencias": ["No se reconoció la sucursal. Selecciónala en los filtros."], "filtros": None}
    try:
        filtros = ReporteRequest(tipo=tipo, fecha_desde=inicio, fecha_hasta=fin, sucursal_id=sucursal_id, solo_bajo_stock="bajo stock" in normal)
    except ValueError:
        return {"interpretado": False, "advertencias": ["El rango de fechas no es válido o supera 366 días."], "filtros": None}
    return {"interpretado": True, "advertencias": [], "texto_normalizado": normal, "filtros": filtros.model_dump(mode="json")}


def _presentar(valor: object) -> object:
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime):
        return valor.astimezone(ZoneInfo("America/La_Paz")).isoformat()
    return valor


def generar_reporte(request: ReporteRequest) -> dict[str, object]:
    sucursales = listar_sucursales()
    if request.sucursal_id is not None and not any(s["id"] == request.sucursal_id for s in sucursales):
        raise HTTPException(status_code=422, detail="La sucursal seleccionada no existe o está inactiva.")
    rows = consultar_reporte(request)
    if len(rows) == 5000:
        raise HTTPException(status_code=422, detail="El reporte alcanza el límite de 5000 filas. Reduce el período o selecciona una sucursal.")
    filas = [{key: _presentar(value) for key, value in row.items()} for row in rows]
    total = sum((Decimal(str(row.get("total", 0) or 0)) for row in rows), Decimal(0))
    unidades = sum(int(row.get("real", row.get("unidades", row.get("cantidad", 0))) or 0) for row in rows)
    bajo_stock = sum(1 for row in rows if row.get("estado") == "BAJO STOCK") if request.tipo == "INVENTARIO" else 0
    serie: dict[str, float] = defaultdict(float)
    if request.tipo in {"VENTAS", "RESERVAS", "MOVIMIENTOS", "TRANSFERENCIAS"}:
        for row in rows:
            fecha = row["fecha"].astimezone(ZoneInfo("America/La_Paz"))
            key = fecha.strftime("%Y-%m" if request.agrupacion == "MES" else "%Y-%m-%d")
            serie[key] += float(row.get("total", 1) or (0 if request.tipo in {"VENTAS", "RESERVAS"} else 1))
    elif request.tipo == "PRODUCTOS_MAS_VENDIDOS":
        serie = {f"{row['producto']} · {row['sku']}": int(row["unidades"]) for row in rows[:10]}
    else:
        serie = {"Bajo stock": bajo_stock, "Stock OK": len(rows) - bajo_stock}
    return {
        "tipo": request.tipo,
        "titulo": TITULOS[request.tipo],
        "nota": "El inventario muestra el estado actual; no existe historial de snapshots para reconstruirlo por fechas." if request.tipo == "INVENTARIO" else "El valor nominal incluye reservas de todos los estados; no equivale a dinero cobrado." if request.tipo == "RESERVAS" else None,
        "filtros_efectivos": {**request.model_dump(mode="json"), "sucursal": next((str(s["nombre"]) for s in sucursales if s["id"] == request.sucursal_id), "Todas")},
        "generado_en": datetime.now(ZoneInfo("America/La_Paz")).isoformat(),
        "indicadores": ([{"label": "Ventas", "valor": len(rows)}, {"label": "Unidades vendidas", "valor": unidades}, {"label": "Total ventas (Bs)", "valor": float(total)}] if request.tipo == "VENTAS" else
                        [{"label": "Reservas", "valor": len(rows)}, {"label": "Unidades solicitadas", "valor": unidades}, {"label": "Valor nominal (Bs)", "valor": float(total)}] if request.tipo == "RESERVAS" else
                        [{"label": "Variantes", "valor": len(rows)}, {"label": "Stock real", "valor": unidades}, {"label": "Bajo stock", "valor": bajo_stock}] if request.tipo == "INVENTARIO" else
                        [{"label": "Registros", "valor": len(rows)}, {"label": "Unidades", "valor": unidades}] if request.tipo in {"PRODUCTOS_MAS_VENDIDOS", "TRANSFERENCIAS"} else
                        [{"label": "Movimientos", "valor": len(rows)}]),
        "serie_grafico": [{"label": key, "valor": value} for key, value in sorted(serie.items())],
        "columnas": [{"key": key, "label": key.replace("_", " ").title()} for key in filas[0]] if filas else [],
        "filas": filas,
        "total_filas": len(filas),
        "sin_datos": not filas,
    }
