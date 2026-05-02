from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.backend.nsi_service.domain.value_objects.position import Position


@dataclass
class Player:
    """Доменная сущность футболиста"""

    id: UUID
    name: str
    first_name: str | None
    last_name: str | None
    date_of_birth: date
    nationality: str
    position: Position
    preferred_foot: str  # "left", "right", "both"
    height_cm: int
    weight_kg: int
    current_club_id: UUID | None
    current_league_id: UUID | None
    market_value: Decimal | None
    contract_until: date | None
    shirt_number: int | None

    # Статистика (агрегируется из матчей)
    appearances: int = field(default=0)
    goals: int = field(default=0)
    assists: int = field(default=0)
    yellow_cards: int = field(default=0)
    red_cards: int = field(default=0)
    minutes_played: int = field(default=0)

    # Продвинутые метрики
    xg: float = field(default=0.0)
    xa: float = field(default=0.0)
    xg_per_90: float = field(default=0.0)
    xa_per_90: float = field(default=0.0)
    tackles_per_90: float = field(default=0.0)

    # Для сравнения и подбора
    league_strength_coefficient: float = field(default=1.0)

    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    @property
    def age(self) -> int:
        """Возраст игрока"""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    @property
    def full_name(self) -> str:
        """Полное имя игрока"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name
