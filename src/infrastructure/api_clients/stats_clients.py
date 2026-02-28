"""Клиенты для внешних статистических платформ"""

from src.infrastructure.api_clients.base_client import BaseStatsClient
from src.infrastructure.api_clients.factory import StatsClientFactory
from src.infrastructure.api_clients.fbref_client import FBRefClient
from src.infrastructure.api_clients.transfermarkt_client import TransfermarktClient
from src.infrastructure.api_clients.understat_client import UnderstatClient

__all__ = [
    "BaseStatsClient",
    "FBRefClient",
    "TransfermarktClient",
    "UnderstatClient",
    "StatsClientFactory",
]
