"""Интерфейсы мапперов для Team"""

from abc import ABC

from src.nsi_service.application.dto.team_dto import TeamDTO
from src.nsi_service.core.mappers.mapper import Mapper
from src.nsi_service.domain.entities.team import Team


class ITeamMapper(Mapper[Team, TeamDTO], ABC):
    """Интерфейс маппера Team"""

    pass
