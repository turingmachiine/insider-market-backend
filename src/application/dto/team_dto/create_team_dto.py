from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class CreateTeamDTO:
    """DTO для создания команды"""

    name: str
    user_id: UUID
    description: Optional[str] = None
