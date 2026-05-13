"""add auth audit logs

Revision ID: 003_audit_logs
Revises: 002_refresh_tokens
Create Date: 2026-05-13
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_audit_logs"
down_revision: str | None = "002_refresh_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Создаем ENUM через сырой SQL с проверкой существования
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'auth_audit_action') THEN
                CREATE TYPE auth_audit_action AS ENUM (
                    'register',
                    'login',
                    'logout',
                    'user_status_update',
                    'role_assignment',
                    'tokens_revoke'
                );
            END IF;
        END $$;
    """
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "action",
            postgresql.ENUM(
                "register",
                "login",
                "logout",
                "user_status_update",
                "role_assignment",
                "tokens_revoke",
                name="auth_audit_action",
                create_type=False,  # Не создаем тип заново
            ),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("before", postgresql.JSONB(), nullable=True),
        sa.Column("after", postgresql.JSONB(), nullable=True),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_correlation_id", "audit_logs", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_correlation_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")

    # Удаляем ENUM через сырой SQL с проверкой
    op.execute("DROP TYPE IF EXISTS auth_audit_action;")
