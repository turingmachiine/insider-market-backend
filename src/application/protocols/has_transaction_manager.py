from typing import Protocol, runtime_checkable

from src.domain.interfaces.transaction_manager import TransactionManager


@runtime_checkable
class HasTransactionManager(Protocol):
    transaction_manager: TransactionManager
