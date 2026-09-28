"""Add email identity for graphical-only accounts.

Revision ID: 0002_user_email
Revises: 0001_initial_persistence
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_user_email"
down_revision: Union[str, Sequence[str], None] = "0001_initial_persistence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=254), nullable=True))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")