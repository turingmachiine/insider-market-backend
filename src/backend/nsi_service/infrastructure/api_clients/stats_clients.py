"""Клиенты для внешних статистических платформ"""

from src.backend.nsi_service.infrastructure.api_clients.base_client import (
    BaseStatsClient,
)
from src.backend.nsi_service.infrastructure.api_clients.factory import (
    StatsClientFactory,
)
from src.backend.nsi_service.infrastructure.api_clients.fbref_client import FBRefClient
from src.backend.nsi_service.infrastructure.api_clients.transfermarkt_client import (
    TransfermarktClient,
)
from src.backend.nsi_service.infrastructure.api_clients.understat_client import (
    UnderstatClient,
)

__all__ = [
    "BaseStatsClient",
    "FBRefClient",
    "TransfermarktClient",
    "UnderstatClient",
    "StatsClientFactory",
]
