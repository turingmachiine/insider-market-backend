"""Интерфейс маппера создания Player"""

from abc import ABC

from src.nsi_service.application.dto.player_dto import CreatePlayerDTO
from src.nsi_service.core.mappers.create_mapper import CreateMapper
from src.nsi_service.domain.entities.player import Player


class ICreatePlayerMapper(CreateMapper[CreatePlayerDTO, Player], ABC):
    """Интерфейс маппера создания Player"""

    pass
