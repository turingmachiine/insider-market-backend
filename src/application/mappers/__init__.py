"""Мапперы сущностей — интерфейсы"""

from src.application.mappers.club_mapper import IClubMapper
from src.application.mappers.create_player_mapper import ICreatePlayerMapper
from src.application.mappers.league_mapper import ILeagueMapper
from src.application.mappers.player_mapper import IPlayerMapper
from src.application.mappers.team_mapper import ITeamMapper
from src.application.mappers.update_player_mapper import IUpdatePlayerMapper

__all__ = [
    "IPlayerMapper",
    "ICreatePlayerMapper",
    "IUpdatePlayerMapper",
    "IClubMapper",
    "ILeagueMapper",
    "ITeamMapper",
]
