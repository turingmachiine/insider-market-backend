from src.market_service.infrastructure.db.tables.audit_logs_table import (
    audit_logs_table,
)
from src.market_service.infrastructure.db.tables.bets_table import bets_table
from src.market_service.infrastructure.db.tables.markets_table import markets_table
from src.market_service.infrastructure.db.tables.positions_table import positions_table
from src.market_service.infrastructure.db.tables.wallets_table import wallets_table

__all__ = [
    "audit_logs_table",
    "bets_table",
    "markets_table",
    "positions_table",
    "wallets_table",
]
