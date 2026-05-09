from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.market_service.domain.entities import Bet, Market, Position, Wallet
from src.market_service.infrastructure.db.metadata import mapper_registry
from src.market_service.infrastructure.db.tables import (
    bets_table,
    markets_table,
    positions_table,
    wallets_table,
)


def setup_mapping() -> None:
    try:
        inspect(Market)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(Market, markets_table)
    mapper_registry.map_imperatively(Bet, bets_table)
    mapper_registry.map_imperatively(Position, positions_table)
    mapper_registry.map_imperatively(Wallet, wallets_table)


__all__ = ["setup_mapping"]
