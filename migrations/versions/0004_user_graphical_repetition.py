"""Add graphical password repetition count and verification tracking to users.

Revision ID: 0004_graphical_repetition
Revises: 0003_graphical_hash_backfill
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_graphical_repetition"
down_revision: Union[str, Sequence[str], None] = "0003_graphical_hash_backfill"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "graphical_password_repetition_count",
            sa.Integer(),
            nullable=False,
            server_default="2",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "graphical_password_verified",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "graphical_password_verified")
    op.drop_column("users", "graphical_password_repetition_count")
