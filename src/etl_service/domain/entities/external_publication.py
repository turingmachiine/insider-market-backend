from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ExternalPublication:
    text: str
    external_id: str | None = None
    url: str | None = None
    published_at: datetime | None = None
    payload: dict[str, Any] = field(default_factory=dict)
