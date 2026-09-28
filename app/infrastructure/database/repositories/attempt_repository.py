from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.attempt import Attempt


class AttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, attempt: Attempt) -> Attempt:
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def list_by_study_session(self, study_session_id: UUID) -> list[Attempt]:
        return list(
            self.session.scalars(
                select(Attempt).where(
                    Attempt.study_session_id == study_session_id
                )
            )
        )
