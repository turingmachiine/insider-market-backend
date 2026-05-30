from typing import Protocol

from src.common.application.scheduling.scheduled_job import ScheduledJob


class IJobComposer(Protocol):
    def compose(self) -> list[ScheduledJob]:
        """Compose configured scheduler jobs."""
