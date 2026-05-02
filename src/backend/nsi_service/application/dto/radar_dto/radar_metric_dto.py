from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RadarMetricDTO:
    """Метрика для радар-чарта"""

    name: str
    value: float
    percentile: float
    league_average: float
    position_average: float
