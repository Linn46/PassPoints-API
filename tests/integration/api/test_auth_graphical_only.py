from collections.abc import Iterator
from uuid import UUID

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.dependencies.authentication as authentication
from app.api.routes.auth import get_auth_service
from app.application.auth.tokens import create_access_token
from app.application.auth.service import AuthService
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.registration import (
    RegistrationAttempt,
    RegistrationDraft,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.database.session import get_db_session
from app.main import app


POINTS = [
    {"x": 214, "y": 173},
    {"x": 843, "y": 921},
    {"x": 1472, "y": 284},
    {"x": 1165, "y": 735},
    {"x": 521, "y": 492},
]
TEST_TOKEN_SECRET = "test-token-secret-" * 3


@pytest.fixture
def auth_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[TestClient, sessionmaker[Session]]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            GraphicalPassword.__table__,
            RegistrationDraft.__table__,
            RegistrationAttempt.__table__,
        ],
    )
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(
        authentication,
        "settings",
        type("TestSettings", (), {"auth_token_secret": TEST_TOKEN_SECRET})(),
    )

    def provide_service() -> Iterator[AuthService]:
        with factory() as session:
            yield AuthService(session, token_secret=TEST_TOKEN_SECRET)

    def provide_db_session() -> Iterator[Session]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_auth_service] = provide_service
    app.dependency_overrides[get_db_session] = provide_db_session
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.pop(get_auth_service, None)
        app.dependency_overrides.pop(get_db_session, None)
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


def complete_registration(client: TestClient, data: dict[str, object]):
    start = client.post("/auth/register", json=data)
    assert start.status_code == 201
    registration_id = start.json()["registration_id"]
    response = None
    for _ in range(2):
        response = client.post(
            f"/auth/register/{registration_id}/repetitions",
            json={"points": POINTS},
        )
    assert response is not None
    return response


def test_registration_is_graphical_only_and_returns_authenticated_session(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client

    response = complete_registration(client, payload())

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["username"] == "demo.user"
    assert body["user"]["email"] == "demo@example.test"
    assert body["access_token"]
    assert "password" not in response.text
    assert "verifier" not in response.text
    claims = jwt.decode(
        body["access_token"], TEST_TOKEN_SECRET, algorithms=["HS256"]
    )
    assert claims["sub"] == body["user"]["id"]
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "demo@example.test"))
        assert user is not None
        assert user.password_hash is not None
        assert user.password_hash.startswith("$argon2id$")
        assert user.graphical_password_repetition_count == 3
        assert user.graphical_password_verified is True
        credential = session.scalar(
            select(GraphicalPassword).where(GraphicalPassword.user_id == user.id)
        )
        assert credential is not None
        assert credential.image_id == "botanical-garden"
        assert credential.verifier.startswith("$argon2id$")
        assert user.password_hash == credential.verifier


def test_registration_records_mismatched_confirmation_and_resets_streak(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client

    start = client.post("/auth/register", json=payload())
    registration_id = start.json()["registration_id"]
    mismatch = [
        {"x": 10, "y": 10},
        {"x": 20, "y": 20},
        {"x": 30, "y": 30},
        {"x": 40, "y": 40},
        {"x": 50, "y": 50},
    ]
    response = client.post(
        f"/auth/register/{registration_id}/repetitions",
        json={"points": mismatch},
    )

    assert response.status_code == 200
    assert response.json()["attempt_correct"] is False
    assert response.json()["consecutive_successes"] == 0
    with factory() as session:
        assert session.scalar(select(User)) is None
        draft = session.get(RegistrationDraft, UUID(registration_id))
        assert draft is not None
        assert [attempt.is_correct for attempt in draft.attempts] == [True, False]


def test_registration_rejects_client_supplied_repetition_count(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client
    invalid_count_request = payload(repetition_count=99)

    response = client.post("/auth/register", json=invalid_count_request)

    assert response.status_code == 422
    with factory() as session:
        assert session.scalar(select(User)) is None
        assert session.scalar(select(GraphicalPassword)) is None


def test_cancelling_registration_discards_candidate_and_restarts_counter(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client
    first = client.post("/auth/register", json=payload()).json()
    first_id = first["registration_id"]
    failed_points = [
        {"x": 10, "y": 10},
        {"x": 20, "y": 20},
        {"x": 30, "y": 30},
        {"x": 40, "y": 40},
        {"x": 50, "y": 50},
    ]
    client.post(
        f"/auth/register/{first_id}/repetitions",
        json={"points": failed_points},
    )

    cancelled = client.delete(f"/auth/register/{first_id}")
    restarted = client.post("/auth/register", json=payload()).json()

    assert cancelled.status_code == 204
    assert restarted["registration_id"] != first_id
    assert restarted["consecutive_successes"] == 1
    with factory() as session:
        assert session.get(RegistrationDraft, UUID(first_id)) is None
        assert session.scalar(select(User)) is None


def test_failed_repetition_requires_three_new_consecutive_successes(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client
    registration = client.post("/auth/register", json=payload()).json()
    registration_id = registration["registration_id"]
    wrong_points = [
        {"x": 10, "y": 10},
        {"x": 20, "y": 20},
        {"x": 30, "y": 30},
        {"x": 40, "y": 40},
        {"x": 50, "y": 50},
    ]
    failed = client.post(
        f"/auth/register/{registration_id}/repetitions",
        json={"points": wrong_points},
    )
    assert failed.json()["consecutive_successes"] == 0

    first = client.post(
        f"/auth/register/{registration_id}/repetitions",
        json={"points": POINTS},
    )
    second = client.post(
        f"/auth/register/{registration_id}/repetitions",
        json={"points": POINTS},
    )
    assert first.json()["consecutive_successes"] == 1
    assert first.json()["completed"] is False
    assert second.json()["consecutive_successes"] == 2
    assert second.json()["completed"] is False
    with factory() as session:
        assert session.scalar(select(User)) is None

    third = client.post(
        f"/auth/register/{registration_id}/repetitions",
        json={"points": POINTS},
    )
    assert third.json()["completed"] is True
    history_response = client.get(
        "/auth/repetition-history",
        headers={"Authorization": f"Bearer {third.json()['access_token']}"},
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["has_history"] is True
    assert history["total_attempts"] == 5
    assert history["failures"] == 1
    assert history["attempts_to_goal"] == 5
    assert [attempt["consecutive_successes"] for attempt in history["attempts"]] == [
        1,
        0,
        1,
        2,
        3,
    ]
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "demo@example.test"))
        draft = session.get(RegistrationDraft, UUID(registration_id))
        assert user is not None
        assert user.graphical_password_repetition_count == 3
        assert draft is not None
        assert [attempt.is_correct for attempt in draft.attempts] == [
            True,
            False,
            True,
            True,
            True,
        ]


def test_login_uses_email_and_graphical_credential(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    complete_registration(client, payload())

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
    complete_registration(client, payload())
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
    complete_registration(client, payload())

    response = client.post("/auth/login", json=login_payload(**overrides))

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_registration_allows_unanalyzed_selection_and_rejects_duplicate_identity(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = auth_client
    grouped_points = [
        {"x": 214, "y": 173},
        {"x": 500, "y": 340},
        {"x": 843, "y": 500},
        {"x": 1165, "y": 735},
        {"x": 1472, "y": 921},
    ]

    unanalyzed = client.post("/auth/register", json=payload(points=grouped_points))
    assert unanalyzed.status_code == 201
    assert client.delete(
        f"/auth/register/{unanalyzed.json()['registration_id']}"
    ).status_code == 204

    assert complete_registration(client, payload()).json()["completed"] is True
    duplicate = client.post(
        "/auth/register", json=payload(username="other.user")
    )
    assert duplicate.status_code == 409


def test_repetition_history_requires_auth_and_shows_legacy_user_without_history(
    auth_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, factory = auth_client
    assert client.get("/auth/repetition-history").status_code == 401
    assert client.get(
        "/auth/repetition-history",
        headers={"Authorization": "Bearer not-a-valid-token"},
    ).status_code == 401

    user = User(username="legacy.user", email="legacy@example.test")
    with factory() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        token = create_access_token(user.id, user.username, TEST_TOKEN_SECRET)

    response = client.get(
        "/auth/repetition-history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "has_history": False,
        "attempts": [],
        "total_attempts": 0,
        "failures": 0,
        "attempts_to_goal": None,
    }