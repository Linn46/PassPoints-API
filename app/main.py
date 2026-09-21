from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.core.config.settings import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para el análisis geométrico y estadístico "
        "de contraseñas gráficas Passpoints."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    analysis_router,
    prefix="/api/v1",
)

app.include_router(health_router)