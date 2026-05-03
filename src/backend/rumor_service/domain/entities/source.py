from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.backend.rumor_service.core.utils.datetime_utils import utc_now


class SourceType(StrEnum):
    TELEGRAM = "telegram"
    MEDIA = "media"
    API = "api"
    MANUAL = "manual"


@dataclass
class Source:
    id: UUID
    name: str
    source_type: SourceType
    handle: str | None = None
    url: str | None = None
    weight: float = 1.0
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
