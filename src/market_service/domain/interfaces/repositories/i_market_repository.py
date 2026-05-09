from abc import ABC, abstractmethod
from uuid import UUID

from src.market_service.domain.entities import Market, MarketStatus


class IMarketRepository(ABC):
    @abstractmethod
    async def get_by_id(self, market_id: UUID) -> Market | None:
        pass

    @abstractmethod
    async def get_by_event_id(self, event_id: UUID) -> Market | None:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: MarketStatus | None = None,
        event_id: UUID | None = None,
    ) -> list[Market]:
        pass

    @abstractmethod
    async def save(self, market: Market) -> Market:
        pass
