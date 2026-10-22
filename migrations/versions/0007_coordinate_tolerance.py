"""Replace Passpoints grid divisions with coordinate-based tolerance.

Revision ID: 0007_coordinate_tolerance
Revises: 0006_registration_attempts
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_coordinate_tolerance"
down_revision: Union[str, Sequence[str], None] = "0006_registration_attempts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM registration_drafts WHERE is_completed = FALSE")
    op.add_column(
        "graphical_passwords",
        sa.Column("encrypted_points", sa.Text(), nullable=True),
    )
    op.add_column(
        "graphical_passwords",
        sa.Column("tolerance_radius", sa.Integer(), server_default="10", nullable=False),
    )
    op.add_column(
        "registration_drafts",
        sa.Column("encrypted_points", sa.Text(), nullable=True),
    )
    op.add_column(
        "registration_drafts",
        sa.Column("tolerance_radius", sa.Integer(), server_default="10", nullable=False),
    )
    op.drop_column("registration_drafts", "tolerance_grid_divisions")
    op.drop_column("users", "tolerance_grid_divisions")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "tolerance_grid_divisions",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
    )
    op.add_column(
        "registration_drafts",
        sa.Column(
            "tolerance_grid_divisions",
            sa.Integer(),
            server_default="5",
            nullable=False,
        ),
    )
    op.drop_column("registration_drafts", "tolerance_radius")
    op.drop_column("registration_drafts", "encrypted_points")
    op.drop_column("graphical_passwords", "tolerance_radius")
    op.drop_column("graphical_passwords", "encrypted_points")
