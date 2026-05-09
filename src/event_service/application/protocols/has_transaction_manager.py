from dataclasses import dataclass

from src.common.domain.interfaces import TransactionManager


@dataclass
class HasTransactionManager:
    transaction_manager: TransactionManager
