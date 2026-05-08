"""initial rating schema

Revision ID: 001_initial_rating
Revises:
Create Date: 2026-05-08
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_rating"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


user_status_enum = postgresql.ENUM(
    "rookie",
    "scout",
    "analyst",
    "expert",
    "legend",
    name="rating_user_status",
    create_type=False,
)
event_type_enum = postgresql.ENUM(
    "prediction_settled",
    "market_created",
    "analysis_published",
    "daily_active",
    "comment_posted",
    name="rating_event_type",
    create_type=False,
)
achievement_rarity_enum = postgresql.ENUM(
    "common",
    "rare",
    "epic",
    "legendary",
    name="rating_achievement_rarity",
    create_type=False,
)
reward_status_enum = postgresql.ENUM(
    "pending",
    "sent",
    "failed",
    name="rating_reward_transaction_status",
    create_type=False,
)


def upgrade() -> None:
    user_status_enum.create(op.get_bind(), checkfirst=True)
    event_type_enum.create(op.get_bind(), checkfirst=True)
    achievement_rarity_enum.create(op.get_bind(), checkfirst=True)
    reward_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "rating_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("status", user_status_enum, nullable=False),
        sa.Column("total_predictions", sa.Integer(), nullable=False),
        sa.Column("correct_predictions", sa.Integer(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("best_streak", sa.Integer(), nullable=False),
        sa.Column("markets_created", sa.Integer(), nullable=False),
        sa.Column("analyses_published", sa.Integer(), nullable=False),
        sa.Column("comments_posted", sa.Integer(), nullable=False),
        sa.Column("active_days", sa.Integer(), nullable=False),
        sa.Column("settled_stake", sa.Numeric(20, 6), nullable=False),
        sa.Column("settled_payout", sa.Numeric(20, 6), nullable=False),
        sa.Column("last_activity_date", sa.Date(), nullable=True),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_calculated_at", sa.DateTime(timezone=True), nullable=True),
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
    op.create_index("ix_rating_profiles_rating", "rating_profiles", ["rating"])
    op.create_index("ix_rating_profiles_status", "rating_profiles", ["status"])

    op.create_table(
        "rating_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", event_type_enum, nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("is_successful", sa.Boolean(), nullable=True),
        sa.Column("stake", sa.Numeric(20, 6), nullable=False),
        sa.Column("payout", sa.Numeric(20, 6), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("idempotency_key", sa.String(length=200), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_rating_events_user_id", "rating_events", ["user_id"])
    op.create_index(
        "ix_rating_events_processed_at",
        "rating_events",
        ["processed_at"],
    )
    op.create_index(
        "ix_rating_events_idempotency_key",
        "rating_events",
        ["idempotency_key"],
        unique=True,
    )

    op.create_table(
        "rating_achievement_definitions",
        sa.Column("code", sa.String(length=100), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metric", sa.String(length=100), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("reward_amount", sa.Numeric(20, 6), nullable=False),
        sa.Column("rarity", achievement_rarity_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "rating_user_achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("achievement_code", sa.String(length=100), nullable=False),
        sa.Column("reward_amount", sa.Numeric(20, 6), nullable=False),
        sa.Column(
            "awarded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "achievement_code",
            name="uq_rating_user_achievements_user_code",
        ),
    )
    op.create_index(
        "ix_rating_user_achievements_user_id",
        "rating_user_achievements",
        ["user_id"],
    )

    op.create_table(
        "rating_reward_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("achievement_code", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(20, 6), nullable=False),
        sa.Column("status", reward_status_enum, nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.String(length=1000), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
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
        "ix_rating_reward_transactions_status",
        "rating_reward_transactions",
        ["status"],
    )
    op.create_index(
        "ix_rating_reward_transactions_idempotency_key",
        "rating_reward_transactions",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_rating_reward_transactions_idempotency_key",
        table_name="rating_reward_transactions",
    )
    op.drop_index(
        "ix_rating_reward_transactions_status",
        table_name="rating_reward_transactions",
    )
    op.drop_table("rating_reward_transactions")
    op.drop_index(
        "ix_rating_user_achievements_user_id",
        table_name="rating_user_achievements",
    )
    op.drop_table("rating_user_achievements")
    op.drop_table("rating_achievement_definitions")
    op.drop_index("ix_rating_events_idempotency_key", table_name="rating_events")
    op.drop_index("ix_rating_events_processed_at", table_name="rating_events")
    op.drop_index("ix_rating_events_user_id", table_name="rating_events")
    op.drop_table("rating_events")
    op.drop_index("ix_rating_profiles_status", table_name="rating_profiles")
    op.drop_index("ix_rating_profiles_rating", table_name="rating_profiles")
    op.drop_table("rating_profiles")
    reward_status_enum.drop(op.get_bind(), checkfirst=True)
    achievement_rarity_enum.drop(op.get_bind(), checkfirst=True)
    event_type_enum.drop(op.get_bind(), checkfirst=True)
    user_status_enum.drop(op.get_bind(), checkfirst=True)
