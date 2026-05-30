from typing import Any, Protocol


class ISchedulerDriver(Protocol):
    def create_scheduler(self) -> Any:
        """Create a scheduler instance for configured jobs."""
