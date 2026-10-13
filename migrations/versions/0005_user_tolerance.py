"""Add tolerance grid divisions to users.

Revision ID: 0005_user_tolerance
Revises: 0004_graphical_repetition
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_user_tolerance"
down_revision: Union[str, Sequence[str], None] = "0004_graphical_repetition"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "tolerance_grid_divisions",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "tolerance_grid_divisions")
