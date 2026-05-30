"""add public rumor fields

Revision ID: 002_public_rumors
Revises: 001_initial_rumor
Create Date: 2026-05-30
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_public_rumors"
down_revision: str | None = "001_initial_rumor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "rumors",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "rumors",
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "rumors",
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE rumors
        SET is_public = TRUE,
            published_at = COALESCE(published_at, updated_at)
        WHERE status = 'approved'
        """
    )
    op.create_index("ix_rumors_event", "rumors", ["event_id"])
    op.create_index("ix_rumors_is_public", "rumors", ["is_public"])
    op.alter_column("rumors", "is_public", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_rumors_is_public", table_name="rumors")
    op.drop_index("ix_rumors_event", table_name="rumors")
    op.drop_column("rumors", "published_at")
    op.drop_column("rumors", "is_public")
    op.drop_column("rumors", "event_id")
