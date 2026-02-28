from abc import ABC

from src.application.dto import LeagueDTO
from src.presentation.api.v1.mappers.base_response_mapper import IBaseResponseMapper
from src.presentation.api.v1.schemas.league_schemas import LeagueResponse


class ILeagueResponseMapper(IBaseResponseMapper[LeagueDTO, LeagueResponse], ABC):
    pass
