from collections.abc import Iterator

import pytest
import jwt
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.api.routes.auth import get_auth_service
from app.api.schemas.auth import GraphicalPointInput
from app.application.auth.service import AuthService
from app.application.passpoints.method import Passpoints
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.user import User
from app.main import app


GRAPHICAL_POINTS = [
    {"x": 214, "y": 173},
    {"x": 843, "y": 921},
    {"x": 1472, "y": 284},
    {"x": 1165, "y": 735},
    {"x": 521, "y": 492},
]


@pytest.fixture
def client_and_session() -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, GraphicalPassword.__table__],
    )
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def provide_auth_service() -> Iterator[AuthService]:
        with factory() as session:
            yield AuthService(session, token_secret="t" * 32)

    app.dependency_overrides[get_auth_service] = provide_auth_service
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.pop(get_auth_service, None)
        engine.dispose()


def register_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "username": "alice",
        "password": "correct horse battery staple",
        "image_id": "image-001",
        "image_width": 1920,
        "image_height": 1080,
        "points": GRAPHICAL_POINTS,
    }
    payload.update(overrides)
    return payload


def login_payload(**overrides: object) -> dict[str, object]:
    return register_payload(**overrides)


def test_register_persists_user_and_graphical_password_without_secrets(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = client_and_session

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 201
    assert set(response.json()) == {"id", "username"}
    assert response.json()["username"] == "alice"
    assert "password" not in response.text
    assert "verifier" not in response.text
    with factory() as session:
        user = session.scalar(select(User).where(User.username == "alice"))
        assert user is not None
        assert user.password_hash != "correct horse battery staple"
        assert user.password_hash.startswith("$argon2id$")
        graphical_passwords = session.scalars(
            select(GraphicalPassword).where(GraphicalPassword.user_id == user.id)
        ).all()
        assert len(graphical_passwords) == 1
        assert graphical_passwords[0].image_id == "image-001"
        assert graphical_passwords[0].verifier.startswith("$argon2id$")
        assert graphical_passwords[0].user_id == user.id


def test_register_uses_passpoints_credential_creation(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = client_and_session
    calls = []
    original = Passpoints.create_credential

    def create_credential(image_id, width, height, points):
        calls.append((image_id, width, height, points))
        return original(image_id, width, height, points)

    monkeypatch.setattr(Passpoints, "create_credential", create_credential)

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 201
    assert len(calls) == 1
    assert calls[0][:3] == ("image-001", 1920, 1080)


def test_register_rejects_duplicate_username(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    assert client.post("/auth/register", json=register_payload()).status_code == 201

    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already registered."}


def test_register_rejects_weak_graphical_pattern(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = client_and_session
    grouped = [
        {"x": 100, "y": 100},
        {"x": 140, "y": 100},
        {"x": 140, "y": 140},
        {"x": 100, "y": 140},
        {"x": 120, "y": 120},
    ]

    response = client.post(
        "/auth/register", json=register_payload(points=grouped)
    )

    assert response.status_code == 422
    with factory() as session:
        assert session.scalar(select(User)) is None
        assert session.scalar(select(GraphicalPassword)) is None


def test_register_rejects_points_in_same_tolerance_cell(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    points = [dict(point) for point in GRAPHICAL_POINTS]
    points[1] = {"x": 215, "y": 174}

    response = client.post("/auth/register", json=register_payload(points=points))

    assert response.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [
        {"username": "a"},
        {"password": "short"},
        {"points": GRAPHICAL_POINTS[:4]},
        {"points": [GRAPHICAL_POINTS[0]] * 5},
        {"unexpected": "field"},
    ],
)
def test_register_rejects_invalid_data(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
    overrides: dict[str, object],
) -> None:
    client, _ = client_and_session

    response = client.post("/auth/register", json=register_payload(**overrides))

    assert response.status_code == 422


def test_graphical_point_schema_rejects_non_finite_coordinates() -> None:
    with pytest.raises(ValidationError):
        GraphicalPointInput(x=float("nan"), y=0.1)


def test_login_returns_bearer_token_without_stored_secrets(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    client.post("/auth/register", json=register_payload())

    response = client.post("/auth/login", json=login_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert data["user"]["username"] == "alice"
    assert "password" not in response.text
    assert "verifier" not in response.text
    assert "password_hash" not in response.text
    claims = jwt.decode(
        data["access_token"], "t" * 32, algorithms=["HS256"]
    )
    assert claims["sub"] == data["user"]["id"]
    assert claims["username"] == "alice"


def test_login_uses_passpoints_verification(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = client_and_session
    client.post("/auth/register", json=register_payload())
    calls = []
    original = Passpoints.verify_credential

    def verify_credential(image_id, width, height, points, verifier):
        calls.append((image_id, width, height))
        return original(image_id, width, height, points, verifier)

    monkeypatch.setattr(Passpoints, "verify_credential", verify_credential)

    response = client.post("/auth/login", json=login_payload())

    assert response.status_code == 200
    assert calls == [("image-001", 1920, 1080)]


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "incorrect password"},
        {"username": "not-registered"},
        {
            "points": [
                {"x": 250, "y": 200},
                *GRAPHICAL_POINTS[1:],
            ]
        },
    ],
)
def test_login_rejects_invalid_credentials(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
    overrides: dict[str, object],
) -> None:
    client, _ = client_and_session
    client.post("/auth/register", json=register_payload())

    response = client.post("/auth/login", json=login_payload(**overrides))

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_login_rejects_inactive_user(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = client_and_session
    client.post("/auth/register", json=register_payload())
    with factory() as session:
        user = session.scalar(select(User).where(User.username == "alice"))
        assert user is not None
        user.is_active = False
        session.commit()

    response = client.post("/auth/login", json=login_payload())

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_login_rejects_different_image(
    client_and_session: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = client_and_session
    client.post("/auth/register", json=register_payload())

    response = client.post(
        "/auth/login", json=login_payload(image_id="different-image")
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}