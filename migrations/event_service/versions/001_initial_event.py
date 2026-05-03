"""initial event schema

Revision ID: 001_initial_event
Revises:
Create Date: 2026-05-03
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_event"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


event_status_enum = postgresql.ENUM(
    "draft",
    "pending_moderation",
    "active",
    "rejected",
    "resolved",
    "cancelled",
    name="event_status",
    create_type=False,
)
event_outcome_enum = postgresql.ENUM(
    "yes",
    "no",
    "void",
    name="event_outcome",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'event_status'
            ) THEN
                CREATE TYPE event_status AS ENUM (
                    'draft',
                    'pending_moderation',
                    'active',
                    'rejected',
                    'resolved',
                    'cancelled'
                );
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'event_outcome'
            ) THEN
                CREATE TYPE event_outcome AS ENUM (
                    'yes',
                    'no',
                    'void'
                );
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", event_status_enum, nullable=False),
        sa.Column("source_rumor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("candidate_payload", postgresql.JSONB(), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_rules", sa.Text(), nullable=True),
        sa.Column("outcome", event_outcome_enum, nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_events_created_at", "events", ["created_at"])
    op.create_index("ix_events_deadline", "events", ["deadline_at"])
    op.create_index("ix_events_source_rumor", "events", ["source_rumor_id"])
    op.create_index("ix_events_status", "events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_source_rumor", table_name="events")
    op.drop_index("ix_events_deadline", table_name="events")
    op.drop_index("ix_events_created_at", table_name="events")
    op.drop_table("events")
    event_outcome_enum.drop(op.get_bind(), checkfirst=True)
    event_status_enum.drop(op.get_bind(), checkfirst=True)
