from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.application.dto.radar_dto.radar_metric_dto import RadarMetricDTO


@dataclass
class PlayerRadarDTO:
    """DTO для радар-чарта игрока"""

    player_id: UUID
    player_name: str
    position: str
    metrics: list[RadarMetricDTO]
    league_name: str
    league_average_metrics: list[RadarMetricDTO]
