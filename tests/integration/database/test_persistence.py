from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models import (
    Attempt,
    GraphicalPassword,
    StudySession,
    User,
)


def new_user() -> User:
    return User(
        username=f"user-{uuid4().hex}",
        password_hash="future-account-password-hash",
    )


def test_alembic_creates_expected_tables(database):
    session = database()
    try:
        table_names = set(inspect(session.bind).get_table_names())
        assert {
            "users",
            "graphical_passwords",
            "study_sessions",
            "attempts",
            "alembic_version",
        }.issubset(table_names)
    finally:
        session.close()


def test_connection_and_user_insertion(database):
    user = new_user()
    session = database()
    try:
        session.add(user)
        session.commit()
        stored_user = session.scalar(select(User).where(User.id == user.id))
        assert stored_user is not None
        assert stored_user.username == user.username
    finally:
        session.close()


def test_username_is_unique(database):
    username = f"unique-{uuid4().hex}"
    session = database()
    try:
        session.add_all(
            [
                User(username=username, password_hash="hash-a"),
                User(username=username, password_hash="hash-b"),
            ]
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    finally:
        session.close()


def test_user_has_graphical_password(database):
    user = new_user()
    graphical_password = GraphicalPassword(
        user=user,
        image_id="image-001",
        verifier="future-verifier-value",
    )
    session = database()
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.graphical_passwords == [graphical_password]
        assert graphical_password.user_id == user.id
    finally:
        session.close()


def test_user_has_study_session(database):
    user = new_user()
    study_session = StudySession(
        user=user,
        started_at=datetime.now(timezone.utc),
    )
    session = database()
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        assert user.study_sessions == [study_session]
        assert study_session.user_id == user.id
    finally:
        session.close()


def test_study_session_has_attempts(database):
    study_session = StudySession(started_at=datetime.now(timezone.utc))
    attempt = Attempt(
        study_session=study_session,
        duration_ms=1200,
        accepted=True,
        weak=False,
        detected_patterns=["regular"],
    )
    session = database()
    try:
        session.add(study_session)
        session.commit()
        session.refresh(study_session)
        assert study_session.attempts == [attempt]
        assert attempt.study_session_id == study_session.id
    finally:
        session.close()


def test_transaction_rollback_discards_user(database):
    user = new_user()
    session = database()
    try:
        session.add(user)
        session.flush()
        user_id = user.id
        session.rollback()
        assert session.get(User, user_id) is None
    finally:
        session.close()
