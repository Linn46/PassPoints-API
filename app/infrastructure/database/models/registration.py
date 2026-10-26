from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class RegistrationDraft(Base):
    __tablename__ = "registration_drafts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    image_id: Mapped[str] = mapped_column(String(255), nullable=False)
    image_width: Mapped[int] = mapped_column(Integer, nullable=False)
    image_height: Mapped[int] = mapped_column(Integer, nullable=False)
    verifier: Mapped[str | None] = mapped_column(Text, nullable=True)
    tolerance_radius: Mapped[int] = mapped_column(Integer, nullable=False)
    max_successful_deviation: Mapped[float] = mapped_column(
        Float, default=0, server_default="0", nullable=False
    )
    encrypted_points: Mapped[str | None] = mapped_column(Text, nullable=True)
    consecutive_successes: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    attempts: Mapped[list["RegistrationAttempt"]] = relationship(
        back_populates="draft",
        cascade="all, delete-orphan",
        order_by="RegistrationAttempt.attempt_number",
    )


class RegistrationAttempt(Base):
    __tablename__ = "registration_attempts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    registration_id: Mapped[UUID] = mapped_column(
        ForeignKey("registration_drafts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    consecutive_successes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    draft: Mapped[RegistrationDraft] = relationship(back_populates="attempts")
