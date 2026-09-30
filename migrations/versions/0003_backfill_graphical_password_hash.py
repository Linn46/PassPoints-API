"""Backfill user password_hash from existing Passpoints verifiers.

Revision ID: 0003_graphical_hash_backfill
Revises: 0002_user_email
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0003_graphical_hash_backfill"
down_revision: Union[str, Sequence[str], None] = "0002_user_email"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE users AS u
        SET password_hash = gp.verifier
        FROM graphical_passwords AS gp
        WHERE gp.user_id = u.id
          AND gp.is_active = TRUE
          AND u.password_hash IS NULL
        """
    )


def downgrade() -> None:
    pass