"""add polymarket event categories

Revision ID: 002_polymarket_event_categories
Revises: 001_initial_event
Create Date: 2026-05-30
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_polymarket_event_categories"
down_revision: str | None = "001_initial_event"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


event_category_enum = postgresql.ENUM(
    "transfers",
    "matches",
    "dismissals",
    "titles",
    "other",
    name="event_category",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'event_category'
            ) THEN
                CREATE TYPE event_category AS ENUM (
                    'transfers',
                    'matches',
                    'dismissals',
                    'titles',
                    'other'
                );
            END IF;
        END
        $$;
        """
    )
    op.add_column(
        "events",
        sa.Column(
            "category",
            event_category_enum,
            nullable=False,
            server_default="other",
        ),
    )
    op.create_index("ix_events_category", "events", ["category"])
    op.alter_column("events", "category", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_events_category", table_name="events")
    op.drop_column("events", "category")
    event_category_enum.drop(op.get_bind(), checkfirst=True)
