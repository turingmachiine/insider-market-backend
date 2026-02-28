"""Интерфейс маппера Player"""

from abc import ABC

from src.application.dto.player_dto import PlayerDTO
from src.core.mappers.mapper import Mapper
from src.domain.entities.player import Player


class IPlayerMapper(Mapper[Player, PlayerDTO], ABC):
    """Интерфейс маппера Player"""

    pass
