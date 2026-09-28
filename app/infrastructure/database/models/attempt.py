from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.study_session import StudySession


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    study_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("study_sessions.id", ondelete="CASCADE"), index=True
    )
    duration_ms: Mapped[int] = mapped_column(Integer)
    accepted: Mapped[bool] = mapped_column(Boolean)
    weak: Mapped[bool] = mapped_column(Boolean)
    detected_patterns: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    study_session: Mapped["StudySession"] = relationship(back_populates="attempts")
