from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.auth import get_auth_service
from app.application.auth.service import AuthService
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.user import User
from app.main import app


IMAGE_IDS = [
    "coast-sunset",
    "botanical-garden",
    "terracotta-house",
    "desert-palms",
    "island-shore",
    "mountain-lake",
    "forest-trail",
    "city-night",
    "coral-reef",
    "snow-cabin",
    "autumn-park",
    "lavender-field",
    "waterfall",
    "lighthouse",
    "red-canyon",
    "night-sky",
    "vineyard",
    "bamboo-grove",
    "harbor",
    "meadow",
    "city-canal",
]
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


def test_login_options_include_registered_image_and_preserve_authentication(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    registration = client.post(
        "/auth/register",
        json={
            "username": "image.user",
            "email": "image@example.test",
            "image_id": "botanical-garden",
            "image_width": 1920,
            "image_height": 1080,
            "points": POINTS,
        },
    )
    assert registration.status_code == 201

    options_response = client.post(
        "/auth/login-images",
        json={
            "email": "IMAGE@example.test",
            "image_ids": IMAGE_IDS,
        },
    )

    assert options_response.status_code == 200
    image_ids = options_response.json()["image_ids"]
    assert len(image_ids) == 3
    assert len(set(image_ids)) == 3
    assert "botanical-garden" in image_ids

    login = client.post(
        "/auth/login",
        json={
            "email": "image@example.test",
            "image_id": "botanical-garden",
            "image_width": 1920,
            "image_height": 1080,
            "points": POINTS,
        },
    )
    assert login.status_code == 200


def test_login_options_for_unknown_email_still_return_three_images(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    response = client.post(
        "/auth/login-images",
        json={
            "email": "unknown@example.test",
            "image_ids": IMAGE_IDS,
        },
    )

    assert response.status_code == 200
    image_ids = response.json()["image_ids"]
    assert len(image_ids) == 3
    assert len(set(image_ids)) == 3
    assert set(image_ids) <= set(IMAGE_IDS)


def test_login_options_reject_insufficient_catalog(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    response = client.post(
        "/auth/login-images",
        json={
            "email": "unknown@example.test",
            "image_ids": ["only-one", "only-two"],
        },
    )

    assert response.status_code == 422


def test_login_options_do_not_substitute_missing_registered_image(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    client.post(
        "/auth/register",
        json={
            "username": "image.user",
            "email": "image@example.test",
            "image_id": "retired-image",
            "image_width": 1920,
            "image_height": 1080,
            "points": POINTS,
        },
    )
    response = client.post(
        "/auth/login-images",
        json={
            "email": "image@example.test",
            "image_ids": IMAGE_IDS,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "The registered image is unavailable in the current catalog."
    )
