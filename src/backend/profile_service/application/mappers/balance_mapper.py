from abc import ABC, abstractmethod

from src.backend.profile_service.application.dto import (
    BalanceTransactionDTO,
    UserBalanceDTO,
)
from src.backend.profile_service.domain.entities import BalanceTransaction, UserBalance


class IBalanceMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(entity: UserBalance) -> UserBalanceDTO:
        pass

    @staticmethod
    @abstractmethod
    def transaction_to_dto(entity: BalanceTransaction) -> BalanceTransactionDTO:
        pass


class BalanceMapper(IBalanceMapper):
    @staticmethod
    def to_dto(entity: UserBalance) -> UserBalanceDTO:
        return UserBalanceDTO(
            id=entity.id,
            user_id=entity.user_id,
            balance=entity.balance,
            reserved_balance=entity.reserved_balance,
            available_balance=entity.available_balance,
            currency=entity.currency,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def transaction_to_dto(entity: BalanceTransaction) -> BalanceTransactionDTO:
        return BalanceTransactionDTO(
            id=entity.id,
            user_id=entity.user_id,
            transaction_type=entity.transaction_type,
            amount=entity.amount,
            balance_after=entity.balance_after,
            reserved_after=entity.reserved_after,
            source=entity.source,
            idempotency_key=entity.idempotency_key,
            metadata=entity.metadata,
            created_at=entity.created_at,
        )
