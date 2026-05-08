from abc import ABC, abstractmethod

from src.backend.market_service.application.dto import WalletDTO
from src.backend.market_service.domain.entities import Wallet


class IWalletMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: Wallet) -> WalletDTO:
        pass


class WalletMapper(IWalletMapper):
    @staticmethod
    def to_dto(entity: Wallet) -> WalletDTO:
        return WalletDTO(
            id=entity.id,
            user_id=entity.user_id,
            balance=entity.balance,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
