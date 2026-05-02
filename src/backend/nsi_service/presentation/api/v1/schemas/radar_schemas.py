"""Pydantic схемы для радар-чартов и похожих игроков"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RadarMetricResponse(BaseModel):
    """Метрика радар-чарта"""

    name: str
    value: float
    percentile: float
    league_average: float
    position_average: float


class PlayerRadarResponse(BaseModel):
    """Радар-чарт игрока"""

    player_id: UUID
    player_name: str
    position: str
    metrics: list[RadarMetricResponse]
    league_name: str
    league_average_metrics: list[RadarMetricResponse]


class SimilarPlayerResponse(BaseModel):
    """Похожий игрок"""

    player_id: UUID
    player_name: str
    position: str
    club_name: str
    league_name: str
    age: int
    nationality: str
    similarity_score: float
    market_value: Optional[Decimal] = None
    key_stats: dict


class SimilarPlayerListResponse(BaseModel):
    """Список похожих игроков"""

    players: list[SimilarPlayerResponse]
