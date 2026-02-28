from abc import ABC

from src.application.dto import TeamDTO
from src.presentation.api.v1.mappers.base_response_mapper import IBaseResponseMapper
from src.presentation.api.v1.schemas.team_schemas import TeamResponse


class ITeamResponseMapper(IBaseResponseMapper[TeamDTO, TeamResponse], ABC):
    pass
