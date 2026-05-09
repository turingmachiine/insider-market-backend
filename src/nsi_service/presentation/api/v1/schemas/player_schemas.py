"""Pydantic схемы для игроков"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
    """Базовая схема игрока"""

    name: str = Field(..., min_length=1, max_length=255, description="Имя игрока")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия")
    nationality: str = Field(..., max_length=100, description="Гражданство")
    position: str = Field(..., description="Позиция на поле")
    preferred_foot: str = Field("right", description="Рабочая нога")
    height_cm: int = Field(180, ge=150, le=220, description="Рост в см")
    weight_kg: int = Field(75, ge=50, le=120, description="Вес в кг")


class PlayerCreate(PlayerBase):
    """Схема создания игрока"""

    date_of_birth: date = Field(..., description="Дата рождения")
    current_club_id: Optional[UUID] = Field(None, description="ID текущего клуба")
    current_league_id: Optional[UUID] = Field(None, description="ID текущей лиги")
    market_value: Optional[Decimal] = Field(None, description="Рыночная стоимость")
    contract_until: Optional[date] = Field(None, description="Контракт до")
    shirt_number: Optional[int] = Field(
        None, ge=1, le=99, description="Номер на футболке"
    )


class PlayerUpdate(BaseModel):
    """Схема обновления игрока"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = None
    preferred_foot: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=150, le=220)
    weight_kg: Optional[int] = Field(None, ge=50, le=120)
    current_club_id: Optional[UUID] = None
    current_league_id: Optional[UUID] = None
    market_value: Optional[Decimal] = None
    contract_until: Optional[date] = None
    shirt_number: Optional[int] = Field(None, ge=1, le=99)


class PlayerResponse(PlayerBase):
    """Схема ответа игрока"""

    model_config = {"from_attributes": True}

    id: UUID
    date_of_birth: date
    current_club_id: Optional[UUID] = None
    current_league_id: Optional[UUID] = None
    market_value: Optional[Decimal] = None
    contract_until: Optional[date] = None
    shirt_number: Optional[int] = None
    appearances: int
    goals: int
    assists: int
    minutes_played: int
    xg: float
    xa: float
    xg_per_90: float
    xa_per_90: float
    league_strength_coefficient: float
    age: int


class PlayerStatsResponse(BaseModel):
    """Схема статистики игрока"""

    player_id: UUID
    player_name: str
    position: str
    appearances: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    minutes_played: int
    goals_per_90: float
    assists_per_90: float
    xg: float
    xa: float
    xg_per_90: float
    xa_per_90: float
