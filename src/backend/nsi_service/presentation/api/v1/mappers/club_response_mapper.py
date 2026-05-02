from abc import ABC

from src.backend.nsi_service.application.dto import ClubDTO
from src.backend.nsi_service.presentation.api.v1.mappers.base_response_mapper import (
    IBaseResponseMapper,
)
from src.backend.nsi_service.presentation.api.v1.schemas.club_schemas import (
    ClubResponse,
)


class IClubResponseMapper(IBaseResponseMapper[ClubDTO, ClubResponse], ABC):
    pass
