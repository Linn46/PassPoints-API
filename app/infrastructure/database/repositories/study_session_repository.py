from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.study_session import StudySession


class StudySessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, study_session: StudySession) -> StudySession:
        self.session.add(study_session)
        self.session.flush()
        return study_session

    def get_by_id(self, session_id: UUID) -> StudySession | None:
        return self.session.get(StudySession, session_id)

    def list_by_user(self, user_id: UUID) -> list[StudySession]:
        return list(
            self.session.scalars(
                select(StudySession).where(StudySession.user_id == user_id)
            )
        )
