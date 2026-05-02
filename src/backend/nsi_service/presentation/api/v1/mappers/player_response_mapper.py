from abc import ABC

from src.backend.nsi_service.application.dto import PlayerDTO
from src.backend.nsi_service.presentation.api.v1.mappers.base_response_mapper import (
    IBaseResponseMapper,
)
from src.backend.nsi_service.presentation.api.v1.schemas.player_schemas import (
    PlayerResponse,
)


class IPlayerResponseMapper(IBaseResponseMapper[PlayerDTO, PlayerResponse], ABC):
    pass
