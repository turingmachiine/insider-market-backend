from abc import ABC

from src.nsi_service.application.dto import LeagueDTO
from src.nsi_service.presentation.api.v1.mappers.base_response_mapper import (
    IBaseResponseMapper,
)
from src.nsi_service.presentation.api.v1.schemas.league_schemas import LeagueResponse


class ILeagueResponseMapper(IBaseResponseMapper[LeagueDTO, LeagueResponse], ABC):
    pass
