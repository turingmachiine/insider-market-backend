from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.backend.admin_service.core.utils.datetime_utils import utc_now


@dataclass
class SavedFilter:
    id: UUID
    actor_user_id: UUID
    name: str
    scope: str
    criteria: dict
    created_at: datetime = field(default_factory=utc_now)
