from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.rumor_service.domain.entities import Rumor, RumorStatus


class IRumorRepository(ABC):
    @abstractmethod
    async def get_by_id(self, rumor_id: UUID) -> Rumor | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: RumorStatus | None = None,
        source_id: UUID | None = None,
    ) -> list[Rumor]:
        pass

    @abstractmethod
    async def save(self, rumor: Rumor) -> Rumor:
        pass
