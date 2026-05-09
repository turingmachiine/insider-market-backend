"""Интерфейс маппера Player"""

from abc import ABC

from src.nsi_service.application.dto.player_dto import PlayerDTO
from src.nsi_service.core.mappers.mapper import Mapper
from src.nsi_service.domain.entities.player import Player


class IPlayerMapper(Mapper[Player, PlayerDTO], ABC):
    """Интерфейс маппера Player"""

    pass
