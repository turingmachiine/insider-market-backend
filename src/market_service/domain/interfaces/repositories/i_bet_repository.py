from abc import ABC, abstractmethod
from uuid import UUID

from src.market_service.domain.entities import Bet


class IBetRepository(ABC):
    @abstractmethod
    async def get_by_market(
        self,
        market_id: UUID,
        limit: int = 100,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[Bet]:
        pass

    @abstractmethod
    async def count_by_market(self, market_id: UUID) -> int:
        pass

    @abstractmethod
    async def save(self, bet: Bet) -> Bet:
        pass
