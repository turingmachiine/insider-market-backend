"""Wrapper схемы для ответов API"""

from pydantic import BaseModel

from src.nsi_service.presentation.api.v1.schemas.club_schemas import ClubResponse
from src.nsi_service.presentation.api.v1.schemas.common_schemas import PaginatedResponse
from src.nsi_service.presentation.api.v1.schemas.league_schemas import LeagueResponse
from src.nsi_service.presentation.api.v1.schemas.player_schemas import PlayerResponse
from src.nsi_service.presentation.api.v1.schemas.radar_schemas import (
    SimilarPlayerResponse,
)
from src.nsi_service.presentation.api.v1.schemas.team_schemas import TeamResponse


class PlayerListResponse(PaginatedResponse):
    """Список игроков"""

    items: list[PlayerResponse]


class ClubListResponse(PaginatedResponse):
    """Список клубов"""

    items: list[ClubResponse]


class LeagueListResponse(PaginatedResponse):
    """Список лиг"""

    items: list[LeagueResponse]


class TeamListResponse(PaginatedResponse):
    """Список команд"""

    items: list[TeamResponse]


class SimilarPlayerListResponse(BaseModel):
    """Список похожих игроков"""

    players: list[SimilarPlayerResponse]
