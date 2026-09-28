from collections.abc import Generator
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config.settings import settings


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_engine_lock = Lock()


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


def get_session_factory() -> sessionmaker[Session]:
    """Returns the process-wide session factory, creating it on first use."""
    global _engine, _session_factory
    if _session_factory is None:
        with _engine_lock:
            if _session_factory is None:
                _engine = create_database_engine()
                _session_factory = sessionmaker(
                    bind=_engine,
                    autoflush=False,
                    expire_on_commit=False,
                )
    return _session_factory


def dispose_database_engine() -> None:
    """Disposes the shared engine when the application shuts down."""
    global _engine, _session_factory
    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
        _engine = None
        _session_factory = None


def get_db_session() -> Generator[Session, None, None]:
    """Provides one request-scoped session and rolls back failed requests."""
    session = get_session_factory()()
    try:
        yield session
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()
