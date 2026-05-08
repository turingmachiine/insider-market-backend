"""initial admin schema

Revision ID: 001_initial_admin
Revises:
Create Date: 2026-05-08
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_admin"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


admin_action_type_enum = postgresql.ENUM(
    "event_approve",
    "event_reject",
    "event_resolve",
    "event_cancel",
    "event_submit",
    "user_status",
    "user_role",
    "filter_create",
    name="admin_action_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'admin_action_type'
            ) THEN
                CREATE TYPE admin_action_type AS ENUM (
                    'event_approve',
                    'event_reject',
                    'event_resolve',
                    'event_cancel',
                    'event_submit',
                    'user_status',
                    'user_role',
                    'filter_create'
                );
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "admin_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", admin_action_type_enum, nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("summary", sa.String(length=200), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_admin_actions_created_at",
        "admin_actions",
        ["created_at"],
    )
    op.create_index(
        "ix_admin_actions_action_type",
        "admin_actions",
        ["action_type"],
    )
    op.create_index(
        "ix_admin_actions_actor_user_id",
        "admin_actions",
        ["actor_user_id"],
    )

    op.create_table(
        "admin_saved_filters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("scope", sa.String(length=120), nullable=False),
        sa.Column("criteria", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_admin_saved_filters_actor_user_id",
        "admin_saved_filters",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_admin_saved_filters_created_at",
        "admin_saved_filters",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_admin_saved_filters_created_at",
        table_name="admin_saved_filters",
    )
    op.drop_index(
        "ix_admin_saved_filters_actor_user_id",
        table_name="admin_saved_filters",
    )
    op.drop_table("admin_saved_filters")
    op.drop_index("ix_admin_actions_actor_user_id", table_name="admin_actions")
    op.drop_index("ix_admin_actions_action_type", table_name="admin_actions")
    op.drop_index("ix_admin_actions_created_at", table_name="admin_actions")
    op.drop_table("admin_actions")
    admin_action_type_enum.drop(op.get_bind(), checkfirst=True)
