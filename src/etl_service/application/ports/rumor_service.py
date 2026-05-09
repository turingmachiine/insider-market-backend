from typing import Protocol
from uuid import UUID

from src.etl_service.application.dto import (
    CreateRawPublicationDTO,
    CreateRumorDTO,
    RawPublicationDTO,
    RumorDTO,
    SourceDTO,
)


class RumorServicePort(Protocol):
    async def get_active_sources(self) -> list[SourceDTO]:
        raise NotImplementedError

    async def get_raw_publications_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RawPublicationDTO]:
        raise NotImplementedError

    async def create_raw_publication(
        self,
        dto: CreateRawPublicationDTO,
    ) -> RawPublicationDTO:
        raise NotImplementedError

    async def get_rumors_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RumorDTO]:
        raise NotImplementedError

    async def create_rumor(self, dto: CreateRumorDTO) -> RumorDTO:
        raise NotImplementedError
