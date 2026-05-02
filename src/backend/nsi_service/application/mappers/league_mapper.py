"""Интерфейсы мапперов для League"""

from abc import ABC

from src.backend.nsi_service.application.dto.league_dto import LeagueDTO
from src.backend.nsi_service.core.mappers.mapper import Mapper
from src.backend.nsi_service.domain.entities.league import League


class ILeagueMapper(Mapper[League, LeagueDTO], ABC):
    """Интерфейс маппера League"""

    pass
