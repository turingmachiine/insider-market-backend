from abc import ABC, abstractmethod
from uuid import UUID

from src.backend.market_service.domain.entities import MarketSide, Position


class IPositionRepository(ABC):
    @abstractmethod
    async def get_by_market_user_side(
        self,
        market_id: UUID,
        user_id: UUID,
        side: MarketSide,
    ) -> Position | None:
        pass

    @abstractmethod
    async def get_by_market(self, market_id: UUID) -> list[Position]:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[Position]:
        pass

    @abstractmethod
    async def save(self, position: Position) -> Position:
        pass
