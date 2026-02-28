from abc import ABC

from src.application.dto import PlayerDTO
from src.presentation.api.v1.mappers.base_response_mapper import IBaseResponseMapper
from src.presentation.api.v1.schemas.player_schemas import PlayerResponse


class IPlayerResponseMapper(IBaseResponseMapper[PlayerDTO, PlayerResponse], ABC):
    pass
