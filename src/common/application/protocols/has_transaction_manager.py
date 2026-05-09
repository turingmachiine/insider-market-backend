from typing import Protocol

from src.common.domain.interfaces import TransactionManager


class HasTransactionManager(Protocol):
    @property
    def transaction_manager(self) -> TransactionManager:  # nosonar
        pass


__all__ = ["HasTransactionManager"]
