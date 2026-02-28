"""API clients module"""

from src.infrastructure.api_clients.data_collection import DataCollectionService
from src.infrastructure.api_clients.stats_clients import (
    BaseStatsClient,
    FBRefClient,
    StatsClientFactory,
    TransfermarktClient,
    UnderstatClient,
)

__all__ = [
    "StatsClientFactory",
    "FBRefClient",
    "TransfermarktClient",
    "UnderstatClient",
    "BaseStatsClient",
    "DataCollectionService",
]
