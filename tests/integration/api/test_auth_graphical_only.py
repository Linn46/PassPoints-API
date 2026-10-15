from collections.abc import Iterator

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.auth import get_auth_service
from app.application.auth.service import AuthService
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.user import User
from app.main import app


POINTS = [
    {"x": 214, "y": 173},
    {"x": 843, "y": 921},
    {"x": 1472, "y": 284},
    {"x": 1165, "y": 735},
    {"x": 521, "y": 492},
]


@pytest.fixture
def auth_client() -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[User.__table__, GraphicalPassword.__table__])
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def provide_service() -> Iterator[AuthService]:
        with factory() as session:
            yield AuthService(session, token_secret="test-token-secret-" * 3)

    app.dependency_overrides[get_auth_service] = provide_service
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.pop(get_auth_service, None)
        engine.dispose()


def payload(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "username": "demo.user",
        "email": "demo@example.test",
        "image_id": "botanical-garden",
        "image_width": 1920,
        "image_height": 1080,
        "points": POINTS,
    }
    data.update(overrides)
    return data


def login_payload(**overrides: object) -> dict[str, object]:
    data = payload()
    data.pop("username")
    data.update(overrides)
    return data


def test_registration_is_graphical_only_and_returns_authenticated_session(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client

    response = client.post("/auth/register", json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["username"] == "demo.user"
    assert body["user"]["email"] == "demo@example.test"
    assert body["access_token"]
    assert "password" not in response.text
    assert "verifier" not in response.text
    claims = jwt.decode(
        body["access_token"], "test-token-secret-" * 3, algorithms=["HS256"]
    )
    assert claims["sub"] == body["user"]["id"]
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "demo@example.test"))
        assert user is not None
        assert user.password_hash is not None
        assert user.password_hash.startswith("$argon2id$")
        credential = session.scalar(
            select(GraphicalPassword).where(GraphicalPassword.user_id == user.id)
        )
        assert credential is not None
        assert credential.image_id == "botanical-garden"
        assert credential.verifier.startswith("$argon2id$")
        assert user.password_hash == credential.verifier


def test_login_uses_email_and_graphical_credential(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    client.post("/auth/register", json=payload())

    response = client.post(
        "/auth/login", json=login_payload(email="DEMO@example.test")
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "demo@example.test"
    assert response.json()["token_type"] == "bearer"


def test_login_backfills_hash_for_existing_graphical_account(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client
    client.post("/auth/register", json=payload())
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "demo@example.test"))
        assert user is not None
        user.password_hash = None
        session.commit()

    response = client.post("/auth/login", json=login_payload())

    assert response.status_code == 200
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "demo@example.test"))
        credential = session.scalar(select(GraphicalPassword))
        assert user is not None
        assert credential is not None
        assert user.password_hash == credential.verifier


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "unknown@example.test"},
        {"image_id": "different-image"},
        {
            "points": [
                {"x": 400, "y": 350},
                *POINTS[1:],
            ]
        },
    ],
)
def test_login_rejects_unknown_or_mismatched_graphical_credential(
    auth_client: tuple[TestClient, sessionmaker[Session]],
    overrides: dict[str, object],
) -> None:
    client, _ = auth_client
    client.post("/auth/register", json=payload())

    response = client.post("/auth/login", json=login_payload(**overrides))

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_registration_rejects_weak_selection_and_duplicate_identity(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    grouped_points = [
        {"x": 100, "y": 100},
        {"x": 140, "y": 100},
        {"x": 140, "y": 140},
        {"x": 100, "y": 140},
        {"x": 120, "y": 120},
    ]

    weak = client.post("/auth/register", json=payload(points=grouped_points))
    assert weak.status_code == 422

    assert client.post("/auth/register", json=payload()).status_code == 201
    duplicate = client.post(
        "/auth/register", json=payload(username="other.user")
    )
    assert duplicate.status_code == 409