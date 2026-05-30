"""add profile publicity flag

Revision ID: 002_profile_publicity
Revises: 001_initial_profile
Create Date: 2026-05-30
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_profile_publicity"
down_revision: str | None = "001_initial_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index("ix_profiles_is_public", "profiles", ["is_public"])
    op.alter_column("profiles", "is_public", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_profiles_is_public", table_name="profiles")
    op.drop_column("profiles", "is_public")
