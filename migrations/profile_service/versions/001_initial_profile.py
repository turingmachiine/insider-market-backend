"""initial profile schema

Revision ID: 001_initial_profile
Revises:
Create Date: 2026-05-08
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_profile"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


activity_type_enum = postgresql.ENUM(
    "profile_created",
    "profile_updated",
    "balance_changed",
    "achievement_awarded",
    "market_bet_placed",
    "market_resolved",
    name="profile_activity_type",
    create_type=False,
)
balance_transaction_type_enum = postgresql.ENUM(
    "credit",
    "debit",
    "reserve",
    "release",
    name="profile_balance_transaction_type",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'profile_activity_type'
            ) THEN
                CREATE TYPE profile_activity_type AS ENUM (
                    'profile_created',
                    'profile_updated',
                    'balance_changed',
                    'achievement_awarded',
                    'market_bet_placed',
                    'market_resolved'
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
                SELECT 1 FROM pg_type
                WHERE typname = 'profile_balance_transaction_type'
            ) THEN
                CREATE TYPE profile_balance_transaction_type AS ENUM (
                    'credit',
                    'debit',
                    'reserve',
                    'release'
                );
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=1000), nullable=True),
        sa.Column("favorite_club", sa.String(length=200), nullable=True),
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
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"], unique=True)

    op.create_table(
        "user_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("balance", sa.Numeric(20, 6), nullable=False),
        sa.Column("reserved_balance", sa.Numeric(20, 6), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
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
    op.create_index(
        "ix_user_balances_user_id",
        "user_balances",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "balance_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", balance_transaction_type_enum, nullable=False),
        sa.Column("amount", sa.Numeric(20, 6), nullable=False),
        sa.Column("balance_after", sa.Numeric(20, 6), nullable=False),
        sa.Column("reserved_after", sa.Numeric(20, 6), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_balance_transactions_user_id",
        "balance_transactions",
        ["user_id"],
    )
    op.create_index(
        "ix_balance_transactions_created_at",
        "balance_transactions",
        ["created_at"],
    )
    op.create_index(
        "ix_balance_transactions_idempotency_key",
        "balance_transactions",
        ["idempotency_key"],
        unique=True,
    )

    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", activity_type_enum, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_activity_type", "activities", ["activity_type"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])

    op.create_table(
        "achievements",
        sa.Column("code", sa.String(length=100), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "user_achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("achievement_code", sa.String(length=100), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column(
            "awarded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "achievement_code",
            name="uq_user_achievements_user_code",
        ),
    )
    op.create_index(
        "ix_user_achievements_user_id",
        "user_achievements",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_user_achievements_user_id", table_name="user_achievements")
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_index("ix_activities_created_at", table_name="activities")
    op.drop_index("ix_activities_activity_type", table_name="activities")
    op.drop_index("ix_activities_user_id", table_name="activities")
    op.drop_table("activities")
    op.drop_index(
        "ix_balance_transactions_idempotency_key",
        table_name="balance_transactions",
    )
    op.drop_index(
        "ix_balance_transactions_created_at", table_name="balance_transactions"
    )
    op.drop_index("ix_balance_transactions_user_id", table_name="balance_transactions")
    op.drop_table("balance_transactions")
    op.drop_index("ix_user_balances_user_id", table_name="user_balances")
    op.drop_table("user_balances")
    op.drop_index("ix_profiles_user_id", table_name="profiles")
    op.drop_table("profiles")
    balance_transaction_type_enum.drop(op.get_bind(), checkfirst=True)
    activity_type_enum.drop(op.get_bind(), checkfirst=True)
