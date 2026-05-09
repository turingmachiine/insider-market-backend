from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class TeamDTO:
    """DTO для передачи данных команды"""

    id: UUID
    name: str
    user_id: UUID
    description: Optional[str]
    squad: dict
    player_count: int
