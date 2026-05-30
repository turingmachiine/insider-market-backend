from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass(frozen=True, slots=True)
class ScheduledJob:
    task_name: str
    schedule_id: str
    labels: dict[str, Any] = field(default_factory=dict)
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    task_id: str | None = None
    cron: str | None = None
    cron_offset: str | timedelta | None = None
    time: datetime | None = None
    interval: int | timedelta | None = None
