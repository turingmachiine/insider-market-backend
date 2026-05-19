"""align nsi uuid columns with runtime mappings

Revision ID: 002_uuid_columns
Revises: 001_initial_nsi
Create Date: 2026-05-19 15:20:00.000000

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_uuid_columns"
down_revision: str | None = "001_initial_nsi"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


FK_CONSTRAINTS = (
    ("player_matches", "player_matches_club_id_fkey"),
    ("player_matches", "player_matches_match_id_fkey"),
    ("player_matches", "player_matches_player_id_fkey"),
    ("matches", "matches_away_club_id_fkey"),
    ("matches", "matches_home_club_id_fkey"),
    ("matches", "matches_league_id_fkey"),
    ("transfers", "transfers_from_club_id_fkey"),
    ("transfers", "transfers_player_id_fkey"),
    ("transfers", "transfers_to_club_id_fkey"),
    ("player_metrics", "player_metrics_player_id_fkey"),
    ("players", "players_current_club_id_fkey"),
    ("players", "players_current_league_id_fkey"),
    ("clubs", "clubs_league_id_fkey"),
)

UUID_COLUMNS = (
    ("leagues", "id"),
    ("clubs", "id"),
    ("clubs", "league_id"),
    ("players", "id"),
    ("players", "current_club_id"),
    ("players", "current_league_id"),
    ("teams", "id"),
    ("teams", "user_id"),
    ("player_metrics", "player_id"),
    ("transfers", "player_id"),
    ("transfers", "from_club_id"),
    ("transfers", "to_club_id"),
    ("matches", "id"),
    ("matches", "home_club_id"),
    ("matches", "away_club_id"),
    ("matches", "league_id"),
    ("player_matches", "player_id"),
    ("player_matches", "match_id"),
    ("player_matches", "club_id"),
)


def _drop_foreign_keys() -> None:
    for table_name, constraint_name in FK_CONSTRAINTS:
        op.drop_constraint(constraint_name, table_name, type_="foreignkey")


def _create_foreign_keys() -> None:
    op.create_foreign_key(
        "clubs_league_id_fkey",
        "clubs",
        "leagues",
        ["league_id"],
        ["id"],
    )
    op.create_foreign_key(
        "players_current_club_id_fkey",
        "players",
        "clubs",
        ["current_club_id"],
        ["id"],
    )
    op.create_foreign_key(
        "players_current_league_id_fkey",
        "players",
        "leagues",
        ["current_league_id"],
        ["id"],
    )
    op.create_foreign_key(
        "player_metrics_player_id_fkey",
        "player_metrics",
        "players",
        ["player_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transfers_player_id_fkey",
        "transfers",
        "players",
        ["player_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transfers_from_club_id_fkey",
        "transfers",
        "clubs",
        ["from_club_id"],
        ["id"],
    )
    op.create_foreign_key(
        "transfers_to_club_id_fkey",
        "transfers",
        "clubs",
        ["to_club_id"],
        ["id"],
    )
    op.create_foreign_key(
        "matches_home_club_id_fkey",
        "matches",
        "clubs",
        ["home_club_id"],
        ["id"],
    )
    op.create_foreign_key(
        "matches_away_club_id_fkey",
        "matches",
        "clubs",
        ["away_club_id"],
        ["id"],
    )
    op.create_foreign_key(
        "matches_league_id_fkey",
        "matches",
        "leagues",
        ["league_id"],
        ["id"],
    )
    op.create_foreign_key(
        "player_matches_player_id_fkey",
        "player_matches",
        "players",
        ["player_id"],
        ["id"],
    )
    op.create_foreign_key(
        "player_matches_match_id_fkey",
        "player_matches",
        "matches",
        ["match_id"],
        ["id"],
    )
    op.create_foreign_key(
        "player_matches_club_id_fkey",
        "player_matches",
        "clubs",
        ["club_id"],
        ["id"],
    )


def _alter_columns_to_uuid() -> None:
    for table_name, column_name in UUID_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.String(length=36),
            type_=postgresql.UUID(),
            postgresql_using=f"{column_name}::uuid",
        )


def _alter_columns_to_string() -> None:
    for table_name, column_name in reversed(UUID_COLUMNS):
        op.alter_column(
            table_name,
            column_name,
            existing_type=postgresql.UUID(),
            type_=sa.String(length=36),
            postgresql_using=f"{column_name}::text",
        )


def upgrade() -> None:
    _drop_foreign_keys()
    _alter_columns_to_uuid()
    _create_foreign_keys()


def downgrade() -> None:
    _drop_foreign_keys()
    _alter_columns_to_string()
    _create_foreign_keys()
