"""add admin action audit fields

Revision ID: 002_admin_action_audit_fields
Revises: 001_initial_admin
Create Date: 2026-05-13
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_admin_action_audit_fields"
down_revision: str | None = "001_initial_admin"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "admin_actions",
        sa.Column("before", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "admin_actions",
        sa.Column("after", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "admin_actions",
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_admin_actions_correlation_id",
        "admin_actions",
        ["correlation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_admin_actions_correlation_id", table_name="admin_actions")
    op.drop_column("admin_actions", "correlation_id")
    op.drop_column("admin_actions", "after")
    op.drop_column("admin_actions", "before")
