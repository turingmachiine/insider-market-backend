"""Интерфейсы мапперов для Club"""

from abc import ABC

from src.application.dto.club_dto import ClubDTO
from src.core.mappers.mapper import Mapper
from src.domain.entities.club import Club


class IClubMapper(Mapper[Club, ClubDTO], ABC):
    """Интерфейс маппера Club"""

    pass
