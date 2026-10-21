"""Persist pending registration attempts until three consecutive successes."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0006_registration_attempts"
down_revision: Union[str, Sequence[str], None] = "0005_user_tolerance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "registration_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("image_id", sa.String(length=255), nullable=False),
        sa.Column("image_width", sa.Integer(), nullable=False),
        sa.Column("image_height", sa.Integer(), nullable=False),
        sa.Column("verifier", sa.Text(), nullable=True),
        sa.Column("tolerance_grid_divisions", sa.Integer(), nullable=False),
        sa.Column(
            "consecutive_successes",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column("attempt_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("is_completed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_registration_drafts_username",
        "registration_drafts",
        ["username"],
    )
    op.create_index(
        "ix_registration_drafts_email",
        "registration_drafts",
        ["email"],
    )
    op.create_table(
        "registration_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("registration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("consecutive_successes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["registration_id"],
            ["registration_drafts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_registration_attempts_registration_id",
        "registration_attempts",
        ["registration_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_registration_attempts_registration_id",
        table_name="registration_attempts",
    )
    op.drop_table("registration_attempts")
    op.drop_index("ix_registration_drafts_email", table_name="registration_drafts")
    op.drop_index("ix_registration_drafts_username", table_name="registration_drafts")
    op.drop_table("registration_drafts")
