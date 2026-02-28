from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass
class Team:
    """
    Доменная сущность "команда пользователя"
    Используется для формирования shadow-team и подбора замен

    squad: dict[str, list[str]] - позиция -> список ID игроков (как строки)
    """

    id: UUID
    name: str
    user_id: UUID
    description: Optional[str] = None

    # Хранит ID игроков как строки для совместимости с JSONB
    squad: dict[str, list[str]] = field(default_factory=dict)

    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)
