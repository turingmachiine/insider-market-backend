"""Интерфейсы мапперов для Club"""

from abc import ABC

from src.nsi_service.application.dto.club_dto import ClubDTO
from src.nsi_service.core.mappers.mapper import Mapper
from src.nsi_service.domain.entities.club import Club


class IClubMapper(Mapper[Club, ClubDTO], ABC):
    """Интерфейс маппера Club"""

    pass
