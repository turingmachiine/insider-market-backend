from typing import Protocol

from src.backend.etl_service.application.dto import SourceDTO
from src.backend.etl_service.domain.entities import ExternalPublication


class PublicationFetcher(Protocol):
    async def fetch(self, source: SourceDTO) -> list[ExternalPublication]:
        raise NotImplementedError
