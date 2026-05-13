"""add market audit logs

Revision ID: 002_audit_logs
Revises: 001_initial_market
Create Date: 2026-05-13
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_audit_logs"
down_revision: str | None = "001_initial_market"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Создаём ENUM только если его нет (через сырой SQL)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'market_audit_action') THEN
                CREATE TYPE market_audit_action AS ENUM (
                    'wallet_create',
                    'bet_place',
                    'market_resolve'
                );
            END IF;
        END $$;
    """
    )

    # 2. Создаём таблицу, указывая create_type=False
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "action",
            postgresql.ENUM(
                "wallet_create",
                "bet_place",
                "market_resolve",
                name="market_audit_action",
                create_type=False,  # ← Ключевой параметр: не создаём тип заново
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

    # 3. Создаём индексы
    op.create_index("ix_market_audit_logs_action", "audit_logs", ["action"])
    op.create_index(
        "ix_market_audit_logs_actor_user_id",
        "audit_logs",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_market_audit_logs_correlation_id",
        "audit_logs",
        ["correlation_id"],
    )


def downgrade() -> None:
    # 1. Удаляем индексы
    op.drop_index("ix_market_audit_logs_correlation_id", table_name="audit_logs")
    op.drop_index("ix_market_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_index("ix_market_audit_logs_action", table_name="audit_logs")

    # 2. Удаляем таблицу
    op.drop_table("audit_logs")

    # 3. Удаляем ENUM, только если он существует и не используется
    op.execute("DROP TYPE IF EXISTS market_audit_action;")
