from abc import ABC, abstractmethod
from uuid import UUID

from src.market_service.domain.entities import Wallet


class IWalletRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Wallet | None:
        pass

    @abstractmethod
    async def save(self, wallet: Wallet) -> Wallet:
        pass
