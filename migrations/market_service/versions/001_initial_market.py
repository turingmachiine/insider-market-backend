"""initial market schema

Revision ID: 001_initial_market
Revises:
Create Date: 2026-05-08
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_market"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


market_status_enum = postgresql.ENUM(
    "draft",
    "active",
    "paused",
    "closed",
    "resolved",
    "cancelled",
    name="market_status",
    create_type=False,
)
market_outcome_enum = postgresql.ENUM(
    "yes",
    "no",
    "void",
    name="market_outcome",
    create_type=False,
)
market_side_enum = postgresql.ENUM(
    "yes",
    "no",
    name="market_side",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'market_status') THEN
                CREATE TYPE market_status AS ENUM (
                    'draft',
                    'active',
                    'paused',
                    'closed',
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
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'market_outcome') THEN
                CREATE TYPE market_outcome AS ENUM ('yes', 'no', 'void');
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'market_side') THEN
                CREATE TYPE market_side AS ENUM ('yes', 'no');
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "markets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("initial_probability", sa.Float(), nullable=False),
        sa.Column("liquidity_parameter", sa.Numeric(20, 6), nullable=False),
        sa.Column("yes_pool", sa.Numeric(20, 6), nullable=False),
        sa.Column("no_pool", sa.Numeric(20, 6), nullable=False),
        sa.Column("status", market_status_enum, nullable=False),
        sa.Column("close_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", market_outcome_enum, nullable=True),
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
    op.create_index("ix_markets_event_id", "markets", ["event_id"], unique=True)
    op.create_index("ix_markets_status", "markets", ["status"])
    op.create_index("ix_markets_close_at", "markets", ["close_at"])

    op.create_table(
        "wallets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("balance", sa.Numeric(20, 6), nullable=False),
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
    op.create_index("ix_wallets_user_id", "wallets", ["user_id"], unique=True)

    op.create_table(
        "bets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("side", market_side_enum, nullable=False),
        sa.Column("amount", sa.Numeric(20, 6), nullable=False),
        sa.Column("shares", sa.Numeric(20, 6), nullable=False),
        sa.Column("probability_before", sa.Float(), nullable=False),
        sa.Column("probability_after", sa.Float(), nullable=False),
        sa.Column("odds_before", sa.Float(), nullable=False),
        sa.Column("odds_after", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_bets_market_id", "bets", ["market_id"])
    op.create_index("ix_bets_user_id", "bets", ["user_id"])
    op.create_index("ix_bets_created_at", "bets", ["created_at"])

    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("side", market_side_enum, nullable=False),
        sa.Column("shares", sa.Numeric(20, 6), nullable=False),
        sa.Column("invested_amount", sa.Numeric(20, 6), nullable=False),
        sa.Column("realized_payout", sa.Numeric(20, 6), nullable=False),
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
        sa.ForeignKeyConstraint(["market_id"], ["markets.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "market_id",
            "user_id",
            "side",
            name="uq_positions_market_user_side",
        ),
    )
    op.create_index("ix_positions_market_id", "positions", ["market_id"])
    op.create_index("ix_positions_user_id", "positions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_positions_user_id", table_name="positions")
    op.drop_index("ix_positions_market_id", table_name="positions")
    op.drop_table("positions")
    op.drop_index("ix_bets_created_at", table_name="bets")
    op.drop_index("ix_bets_user_id", table_name="bets")
    op.drop_index("ix_bets_market_id", table_name="bets")
    op.drop_table("bets")
    op.drop_index("ix_wallets_user_id", table_name="wallets")
    op.drop_table("wallets")
    op.drop_index("ix_markets_close_at", table_name="markets")
    op.drop_index("ix_markets_status", table_name="markets")
    op.drop_index("ix_markets_event_id", table_name="markets")
    op.drop_table("markets")
    market_side_enum.drop(op.get_bind(), checkfirst=True)
    market_outcome_enum.drop(op.get_bind(), checkfirst=True)
    market_status_enum.drop(op.get_bind(), checkfirst=True)
