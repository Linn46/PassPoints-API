from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config.settings import settings


def create_database_engine(database_url: str | None = None) -> Engine:
    """Crea el engine de base de datos a partir de la configuración."""
    url = database_url or settings.database_url
    if not url:
        raise RuntimeError(
            "DATABASE_URL no está configurada. "
            "Define una URL PostgreSQL antes de usar la persistencia."
        )
    return create_engine(url, pool_pre_ping=True)


def create_session_factory(
    database_url: str | None = None,
) -> sessionmaker[Session]:
    """Crea una fábrica de sesiones independiente para cada contexto."""
    return sessionmaker(
        bind=create_database_engine(database_url),
        autoflush=False,
        expire_on_commit=False,
    )


def get_db_session() -> Generator[Session, None, None]:
    """Proporciona una sesión con commit/rollback gestionado por el llamador."""
    session_factory = create_session_factory()
    with session_factory() as session:
        yield session
