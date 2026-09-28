import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "Los tests de persistencia requieren DATABASE_URL. "
            "Configura PostgreSQL y exporta esa variable antes de ejecutarlos."
        )
    return database_url


@pytest.fixture(scope="session")
def database(database_url: str) -> Iterator[sessionmaker[Session]]:
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        engine.dispose()
        command.downgrade(alembic_config, "-1")
