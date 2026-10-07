from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.exception_handlers import (
    delaunay_validation_error_handler,
    request_validation_error_handler,
)
from app.core.config.settings import settings
from app.geometry.delaunay.validator import DelaunayValidationError
from app.infrastructure.database.session import dispose_database_engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        dispose_database_engine()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para el análisis geométrico y estadístico "
        "de contraseñas gráficas Passpoints."
    ),
    lifespan=lifespan,
)

app.add_exception_handler(
    DelaunayValidationError,
    delaunay_validation_error_handler,
)

app.add_exception_handler(
    RequestValidationError,
    request_validation_error_handler,
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
app.include_router(auth_router)