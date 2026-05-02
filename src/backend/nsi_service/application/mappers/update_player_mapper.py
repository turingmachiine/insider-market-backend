"""Интерфейс маппера обновления Player"""

from abc import ABC

from src.backend.nsi_service.application.dto.player_dto import UpdatePlayerDTO
from src.backend.nsi_service.core.mappers.update_mapper import UpdateMapper
from src.backend.nsi_service.domain.entities.player import Player


class IUpdatePlayerMapper(UpdateMapper[UpdatePlayerDTO, Player], ABC):
    """Интерфейс маппера обновления Player"""

    pass
