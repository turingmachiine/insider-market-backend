"""Pydantic схемы для команд"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    """Базовая схема команды"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class TeamCreate(TeamBase):
    """Схема создания команды"""

    pass


class TeamResponse(TeamBase):
    """Схема ответа команды"""

    model_config = {"from_attributes": True}

    id: UUID
    user_id: UUID
    squad: dict
    player_count: int


class AddPlayerToTeamRequest(BaseModel):
    """Запрос добавления игрока в команду"""

    position: str = Field(..., description="Позиция на поле")
    player_id: UUID = Field(..., description="ID игрока")
