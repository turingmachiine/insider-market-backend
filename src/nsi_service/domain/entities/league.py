from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class League:
    """Доменная сущность лиги/турнира"""

    id: UUID
    name: str
    short_name: Optional[str]
    country: str
    tier: int  # Уровень лиги (1 - топ, 2, 3 и т.д.)
    confederation: str  # UEFA, CONMEBOL, etc.
    logo_url: Optional[str]
    strength_coefficient: float = field(default=1.0)
    current_season: Optional[str] = None
    season_start: Optional[date] = None
    season_end: Optional[date] = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    @property
    def display_name(self) -> str:
        """Отображаемое имя лиги"""
        return self.short_name or self.name

    @property
    def is_top_league(self) -> bool:
        """Является ли лига топ-5"""
        return self.tier == 1
