from typing import Protocol, runtime_checkable

from src.backend.nsi_service.domain.interfaces.transaction_manager import (
    TransactionManager,
)


@runtime_checkable
class HasTransactionManager(Protocol):
    transaction_manager: TransactionManager
