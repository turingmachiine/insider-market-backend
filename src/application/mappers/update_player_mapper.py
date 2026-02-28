"""Интерфейс маппера обновления Player"""

from abc import ABC

from src.application.dto.player_dto import UpdatePlayerDTO
from src.core.mappers.update_mapper import UpdateMapper
from src.domain.entities.player import Player


class IUpdatePlayerMapper(UpdateMapper[UpdatePlayerDTO, Player], ABC):
    """Интерфейс маппера обновления Player"""

    pass
