"""Initial tables creation

Revision ID: 001_initial
Revises:
Create Date: 2026-02-22 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create leagues table
    op.create_table(
        "leagues",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("short_name", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("tier", sa.Integer, nullable=False, default=1),
        sa.Column("confederation", sa.String(50), nullable=False, default="UEFA"),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("strength_coefficient", sa.Float, nullable=False, default=1.0),
        sa.Column("current_season", sa.String(50), nullable=True),
        sa.Column("season_start", sa.Date, nullable=True),
        sa.Column("season_end", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leagues_country", "leagues", ["country"], unique=False)
    op.create_index("ix_leagues_tier", "leagues", ["tier"], unique=False)

    # Create clubs table
    op.create_table(
        "clubs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("short_name", sa.String(100), nullable=True),
        sa.Column("founded_year", sa.Integer, nullable=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("stadium_name", sa.String(255), nullable=True),
        sa.Column("stadium_capacity", sa.Integer, nullable=True),
        sa.Column(
            "league_id", sa.String(36), sa.ForeignKey("leagues.id"), nullable=True
        ),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("squad_market_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("average_age", sa.Float, nullable=True),
        sa.Column("foreign_players_count", sa.Integer, nullable=True),
        sa.Column("national_team_players_count", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clubs_name", "clubs", ["name"], unique=False)
    op.create_index("ix_clubs_league", "clubs", ["league_id"], unique=False)
    op.create_index("ix_clubs_country", "clubs", ["country"], unique=False)

    # Create players table
    op.create_table(
        "players",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=False),
        sa.Column("nationality", sa.String(100), nullable=False),
        sa.Column("position", sa.String(50), nullable=False),
        sa.Column("preferred_foot", sa.String(20), nullable=False, default="right"),
        sa.Column("height_cm", sa.Integer, nullable=False),
        sa.Column("weight_kg", sa.Integer, nullable=False),
        sa.Column(
            "current_club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=True
        ),
        sa.Column(
            "current_league_id",
            sa.String(36),
            sa.ForeignKey("leagues.id"),
            nullable=True,
        ),
        sa.Column("market_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("contract_until", sa.Date, nullable=True),
        sa.Column("shirt_number", sa.Integer, nullable=True),
        sa.Column("appearances", sa.Integer, nullable=False, default=0),
        sa.Column("goals", sa.Integer, nullable=False, default=0),
        sa.Column("assists", sa.Integer, nullable=False, default=0),
        sa.Column("yellow_cards", sa.Integer, nullable=False, default=0),
        sa.Column("red_cards", sa.Integer, nullable=False, default=0),
        sa.Column("minutes_played", sa.Integer, nullable=False, default=0),
        sa.Column("xg", sa.Float, nullable=False, default=0.0),
        sa.Column("xa", sa.Float, nullable=False, default=0.0),
        sa.Column("xg_per_90", sa.Float, nullable=False, default=0.0),
        sa.Column("xa_per_90", sa.Float, nullable=False, default=0.0),
        sa.Column("league_strength_coefficient", sa.Float, nullable=False, default=1.0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_name", "players", ["name"], unique=False)
    op.create_index("ix_players_position", "players", ["position"], unique=False)
    op.create_index("ix_players_club", "players", ["current_club_id"], unique=False)
    op.create_index("ix_players_league", "players", ["current_league_id"], unique=False)
    op.create_index("ix_players_nationality", "players", ["nationality"], unique=False)

    # Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("squad", sa.JSON, nullable=True),  # JSONB для dict, nullable
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_user", "teams", ["user_id"], unique=False)
    op.create_index("ix_teams_name", "teams", ["name"], unique=False)

    # Create raw_stats table
    op.create_table(
        "raw_stats",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("data", sa.Text, nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed", sa.Boolean, nullable=False, default=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_stats_source", "raw_stats", ["source"], unique=False)
    op.create_index(
        "ix_raw_stats_entity", "raw_stats", ["entity_type", "entity_id"], unique=False
    )
    op.create_index("ix_raw_stats_processed", "raw_stats", ["processed"], unique=False)

    # Create player_metrics table
    op.create_table(
        "player_metrics",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column(
            "player_id", sa.String(36), sa.ForeignKey("players.id"), nullable=False
        ),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Float, nullable=False),
        sa.Column("percentile", sa.Float, nullable=True),
        sa.Column("league_average", sa.Float, nullable=True),
        sa.Column("position_average", sa.Float, nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_player_metrics_player", "player_metrics", ["player_id"], unique=False
    )
    op.create_index(
        "ix_player_metrics_name", "player_metrics", ["metric_name"], unique=False
    )

    # Create transfers table
    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column(
            "player_id", sa.String(36), sa.ForeignKey("players.id"), nullable=False
        ),
        sa.Column(
            "from_club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=True
        ),
        sa.Column(
            "to_club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=False
        ),
        sa.Column("transfer_date", sa.Date, nullable=False),
        sa.Column("transfer_fee", sa.Numeric(15, 2), nullable=True),
        sa.Column("transfer_type", sa.String(50), nullable=False),
        sa.Column("season", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transfers_player", "transfers", ["player_id"], unique=False)
    op.create_index("ix_transfers_date", "transfers", ["transfer_date"], unique=False)

    # Create matches table
    op.create_table(
        "matches",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column(
            "home_club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=False
        ),
        sa.Column(
            "away_club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=False
        ),
        sa.Column(
            "league_id", sa.String(36), sa.ForeignKey("leagues.id"), nullable=True
        ),
        sa.Column("match_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("home_score", sa.Integer, nullable=True),
        sa.Column("away_score", sa.Integer, nullable=True),
        sa.Column("season", sa.String(50), nullable=False),
        sa.Column("round", sa.String(50), nullable=True),
        sa.Column("venue", sa.String(255), nullable=True),
        sa.Column("attendance", sa.Integer, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="scheduled"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_date", "matches", ["match_date"], unique=False)
    op.create_index("ix_matches_league", "matches", ["league_id"], unique=False)
    op.create_index(
        "ix_matches_clubs", "matches", ["home_club_id", "away_club_id"], unique=False
    )

    # Create player_matches table
    op.create_table(
        "player_matches",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column(
            "player_id", sa.String(36), sa.ForeignKey("players.id"), nullable=False
        ),
        sa.Column(
            "match_id", sa.String(36), sa.ForeignKey("matches.id"), nullable=False
        ),
        sa.Column("club_id", sa.String(36), sa.ForeignKey("clubs.id"), nullable=False),
        sa.Column("position", sa.String(50), nullable=False),
        sa.Column("minutes_played", sa.Integer, nullable=False, default=0),
        sa.Column("goals", sa.Integer, nullable=False, default=0),
        sa.Column("assists", sa.Integer, nullable=False, default=0),
        sa.Column("yellow_cards", sa.Integer, nullable=False, default=0),
        sa.Column("red_cards", sa.Integer, nullable=False, default=0),
        sa.Column("xg", sa.Float, nullable=False, default=0.0),
        sa.Column("xa", sa.Float, nullable=False, default=0.0),
        sa.Column("rating", sa.Float, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_player_matches_player", "player_matches", ["player_id"], unique=False
    )
    op.create_index(
        "ix_player_matches_match", "player_matches", ["match_id"], unique=False
    )


def downgrade() -> None:
    op.drop_table("player_matches")
    op.drop_table("matches")
    op.drop_table("transfers")
    op.drop_table("player_metrics")
    op.drop_table("raw_stats")
    op.drop_table("teams")
    op.drop_table("players")
    op.drop_table("clubs")
    op.drop_table("leagues")
