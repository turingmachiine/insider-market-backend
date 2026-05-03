from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.event_service.domain.entities import Event, EventStatus


class IEventRepository(ABC):
    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Event | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: EventStatus | None = None,
        source_rumor_id: UUID | None = None,
    ) -> list[Event]:
        pass

    @abstractmethod
    async def save(self, event: Event) -> Event:
        pass
