from abc import ABC, abstractmethod
from uuid import UUID

from src.event_service.domain.entities import (
    Event,
    EventCategory,
    EventSort,
    EventStatus,
)


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
        category: EventCategory | None = None,
        sort: EventSort = EventSort.CREATED_AT,
    ) -> list[Event]:
        pass

    @abstractmethod
    async def save(self, event: Event) -> Event:
        pass
