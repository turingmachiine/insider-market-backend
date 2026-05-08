from dataclasses import dataclass, field
from datetime import datetime

from src.backend.profile_service.core.utils.datetime_utils import utc_now


@dataclass
class Achievement:
    code: str
    name: str
    description: str
    icon_url: str | None = None
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.code = self.code.strip().lower()
        self.name = self.name.strip()
        self.description = self.description.strip()
        if not self.code:
            raise ValueError("Achievement code must not be empty")
        if not self.name:
            raise ValueError("Achievement name must not be empty")
