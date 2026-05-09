from abc import ABC, abstractmethod
from uuid import UUID

from src.rumor_service.domain.entities import RawPublication


class IRawPublicationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, publication_id: UUID) -> RawPublication | None:
        pass

    @abstractmethod
    async def get_by_external_id(
        self,
        source_id: UUID,
        external_id: str,
    ) -> RawPublication | None:
        pass

    @abstractmethod
    async def get_by_source(
        self,
        source_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RawPublication]:
        pass

    @abstractmethod
    async def save(self, publication: RawPublication) -> RawPublication:
        pass
