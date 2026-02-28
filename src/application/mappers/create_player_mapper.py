"""Интерфейс маппера создания Player"""

from abc import ABC

from src.application.dto.player_dto import CreatePlayerDTO
from src.core.mappers.create_mapper import CreateMapper
from src.domain.entities.player import Player


class ICreatePlayerMapper(CreateMapper[CreatePlayerDTO, Player], ABC):
    """Интерфейс маппера создания Player"""

    pass
