"""Track successful registration deviations for adaptive tolerance.

Revision ID: 0008_adaptive_tolerance
Revises: 0007_coordinate_tolerance
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_adaptive_tolerance"
down_revision: Union[str, Sequence[str], None] = "0007_coordinate_tolerance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "registration_drafts",
        sa.Column(
            "max_successful_deviation",
            sa.Float(),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("registration_drafts", "max_successful_deviation")
