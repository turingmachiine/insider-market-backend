from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass
class Club:
    """Доменная сущность футбольного клуба"""

    id: UUID
    name: str
    short_name: Optional[str]
    founded_year: Optional[int]
    country: str
    city: str
    stadium_name: Optional[str]
    stadium_capacity: Optional[int]
    league_id: Optional[UUID]
    logo_url: Optional[str]
    website: Optional[str]

    # Стоимость состава
    squad_market_value: Optional[Decimal]
    average_age: Optional[float]
    foreign_players_count: Optional[int]
    national_team_players_count: Optional[int]

    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    @property
    def display_name(self) -> str:
        """Отображаемое имя клуба"""
        return self.short_name or self.name
