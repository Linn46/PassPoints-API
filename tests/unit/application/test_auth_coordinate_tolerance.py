from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.schemas.auth import RegisterRequest
from app.application.auth.service import AuthService, InvalidAuthenticationError
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.registration import (
    RegistrationAttempt,
    RegistrationDraft,
)
from app.infrastructure.database.models.user import User


IMAGE = "botanical-garden"
WIDTH = 1920
HEIGHT = 1080
SECRET = "auth-coordinate-test-secret-over-32-bytes"
POINTS = [
    (432, 162),
    (654, 367),
    (1422, 799),
    (1038, 583),
    (462, 907),
]


@pytest.fixture
def auth_service() -> Iterator[tuple[AuthService, Session]]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            GraphicalPassword.__table__,
            RegistrationDraft.__table__,
            RegistrationAttempt.__table__,
        ],
    )
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield AuthService(session, token_secret=SECRET), session
    finally:
        session.close()
        engine.dispose()


def test_tolerance_is_learned_from_confirmations_and_used_for_login(
    auth_service: tuple[AuthService, Session],
) -> None:
    service, session = auth_service
    progress = service.start_registration(
        "alice",
        "alice@example.com",
        IMAGE,
        WIDTH,
        HEIGHT,
        POINTS,
    )
    repeated = [(x + 17, y) for x, y in POINTS]

    service.register_repetition(progress.registration_id, repeated)
    completed = service.register_repetition(progress.registration_id, repeated)

    assert completed.user is not None
    credential = session.scalar(select(GraphicalPassword))
    assert credential is not None
    assert credential.tolerance_radius == 19
    assert credential.encrypted_points
    user, _, _ = service.login(
        "alice@example.com", IMAGE, WIDTH, HEIGHT, repeated
    )
    assert user.id == completed.user.id

    outside_radius = [(x + 20, y) for x, y in POINTS]
    with pytest.raises(InvalidAuthenticationError):
        service.login("alice@example.com", IMAGE, WIDTH, HEIGHT, outside_radius)


def test_registration_rejects_manual_tolerance_input() -> None:
    with pytest.raises(ValueError):
        RegisterRequest(
            username="alice",
            email="alice@example.com",
            image_id=IMAGE,
            image_width=WIDTH,
            image_height=HEIGHT,
            points=[{"x": x, "y": y} for x, y in POINTS],
            tolerance_radius=30,
        )


def test_registration_requires_confirmation_or_staged_repetition() -> None:
    with pytest.raises(ValueError, match="confirmation is required"):
        RegisterRequest(
            username="alice",
            email="alice@example.com",
            image_id=IMAGE,
            image_width=WIDTH,
            image_height=HEIGHT,
            points=[{"x": x, "y": y} for x, y in POINTS],
        )


def test_registration_schema_accepts_two_confirmation_sequences() -> None:
    request = RegisterRequest(
        username="alice",
        email="alice@example.com",
        image_id=IMAGE,
        image_width=WIDTH,
        image_height=HEIGHT,
        points=[{"x": x, "y": y} for x, y in POINTS],
        confirmation_points=[
            [{"x": x + 5, "y": y} for x, y in POINTS],
            [{"x": x + 8, "y": y} for x, y in POINTS],
        ],
    )

    assert len(request.confirmation_points) == 2


def test_registration_schema_rejects_duplicate_confirmation_points() -> None:
    with pytest.raises(ValueError):
        RegisterRequest(
            username="alice",
            email="alice@example.com",
            image_id=IMAGE,
            image_width=WIDTH,
            image_height=HEIGHT,
            points=[{"x": x, "y": y} for x, y in POINTS],
            confirmation_points=[
                [{"x": 100, "y": 100}] * 5,
                [{"x": x, "y": y} for x, y in POINTS],
            ],
        )


def test_immediate_registration_persists_calibrated_tolerance(
    auth_service: tuple[AuthService, Session],
) -> None:
    service, session = auth_service
    confirmations = [
        [(x + 16, y) for x, y in POINTS],
        [(x + 20, y) for x, y in POINTS],
    ]

    completed = service.register_immediately(
        "alice",
        "alice@example.com",
        IMAGE,
        WIDTH,
        HEIGHT,
        POINTS,
        confirmations,
    )

    assert completed.user is not None
    credential = session.scalar(select(GraphicalPassword))
    assert credential is not None
    assert credential.tolerance_radius == 22
    user, _, _ = service.login(
        "alice@example.com",
        IMAGE,
        WIDTH,
        HEIGHT,
        [(x + 21, y) for x, y in POINTS],
    )
    assert user.id == completed.user.id
