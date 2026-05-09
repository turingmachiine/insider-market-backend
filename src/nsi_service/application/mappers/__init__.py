"""Мапперы сущностей — интерфейсы"""

from src.nsi_service.application.mappers.club_mapper import IClubMapper
from src.nsi_service.application.mappers.create_player_mapper import ICreatePlayerMapper
from src.nsi_service.application.mappers.league_mapper import ILeagueMapper
from src.nsi_service.application.mappers.player_mapper import IPlayerMapper
from src.nsi_service.application.mappers.team_mapper import ITeamMapper
from src.nsi_service.application.mappers.update_player_mapper import IUpdatePlayerMapper

__all__ = [
    "IPlayerMapper",
    "ICreatePlayerMapper",
    "IUpdatePlayerMapper",
    "IClubMapper",
    "ILeagueMapper",
    "ITeamMapper",
]
