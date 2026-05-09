"""Реализации мапперов на основе adaptix"""

from src.nsi_service.infrastructure.adaptix.club_mapper import ClubMapperImpl
from src.nsi_service.infrastructure.adaptix.league_mapper import LeagueMapperImpl
from src.nsi_service.infrastructure.adaptix.player_mapper import (
    CreatePlayerMapperImpl,
    PlayerMapperImpl,
    UpdatePlayerMapperImpl,
)
from src.nsi_service.infrastructure.adaptix.team_mapper import TeamMapperImpl

__all__ = [
    "PlayerMapperImpl",
    "CreatePlayerMapperImpl",
    "UpdatePlayerMapperImpl",
    "ClubMapperImpl",
    "LeagueMapperImpl",
    "TeamMapperImpl",
]
