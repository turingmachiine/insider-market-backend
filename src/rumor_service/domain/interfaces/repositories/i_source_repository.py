from abc import ABC, abstractmethod
from uuid import UUID

from src.rumor_service.domain.entities import Source


class ISourceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, source_id: UUID) -> Source | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Source | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        active_only: bool = False,
    ) -> list[Source]:
        pass

    @abstractmethod
    async def save(self, source: Source) -> Source:
        pass
