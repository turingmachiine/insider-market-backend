"""Интерфейсы мапперов для Team"""

from abc import ABC

from src.application.dto.team_dto import TeamDTO
from src.core.mappers.mapper import Mapper
from src.domain.entities.team import Team


class ITeamMapper(Mapper[Team, TeamDTO], ABC):
    """Интерфейс маппера Team"""

    pass
