"""Интерфейсы мапперов для League"""

from abc import ABC

from src.application.dto.league_dto import LeagueDTO
from src.core.mappers.mapper import Mapper
from src.domain.entities.league import League


class ILeagueMapper(Mapper[League, LeagueDTO], ABC):
    """Интерфейс маппера League"""

    pass
