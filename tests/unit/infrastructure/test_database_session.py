from sqlalchemy import create_engine

from app.infrastructure.database import session as database_session


def test_session_factory_reuses_engine_until_disposed(monkeypatch) -> None:
    database_session.dispose_database_engine()
    engines = []

    def create_test_engine(database_url=None):
        engine = create_engine("sqlite://")
        engines.append(engine)
        return engine

    monkeypatch.setattr(
        database_session, "create_database_engine", create_test_engine
    )

    first_factory = database_session.get_session_factory()
    second_factory = database_session.get_session_factory()

    assert first_factory is second_factory
    assert len(engines) == 1

    database_session.dispose_database_engine()
    third_factory = database_session.get_session_factory()

    assert third_factory is not first_factory
    assert len(engines) == 2

    database_session.dispose_database_engine()