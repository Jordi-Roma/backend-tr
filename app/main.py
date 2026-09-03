from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import get_connection
from app.modules.administracion_comercial.router.ciudad_sucursal_router import (
    router as ciudad_sucursal_router,
)
from app.modules.administracion_comercial.router.empleado_router import (
    router as empleado_router,
)
from app.modules.autenticacion.router.perfil_router import router as perfil_router
from app.modules.autenticacion.router.registro_router import router as registro_router
from app.modules.autenticacion.router.rol_permiso_router import (
    router as rol_permiso_router,
)
from app.modules.autenticacion.router.sesion_router import router as sesion_router
from app.modules.autenticacion.router.usuario_admin_router import (
    router as usuario_admin_router,
)


app = FastAPI(
    title="API Tienda de Ropa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(registro_router)
app.include_router(sesion_router)
app.include_router(perfil_router)
app.include_router(rol_permiso_router)
app.include_router(usuario_admin_router)
app.include_router(ciudad_sucursal_router)
app.include_router(empleado_router)


@app.get("/api/v1/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "backend-tr",
    }


@app.get("/api/v1/db-check")
def db_check() -> dict[str, str]:
    connection = get_connection()
    connection.close()

    return {
        "status": "ok",
        "database": "connected",
    }
