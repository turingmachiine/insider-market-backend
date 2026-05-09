from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from src.rumor_service.core.utils.datetime_utils import utc_now


@dataclass
class RawPublication:
    id: UUID
    source_id: UUID
    text: str
    external_id: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = field(default_factory=utc_now)
    payload: dict[str, Any] = field(default_factory=dict)
