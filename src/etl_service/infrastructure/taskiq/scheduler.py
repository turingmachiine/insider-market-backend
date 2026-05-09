from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from src.etl_service.infrastructure.taskiq.broker import broker

# Import tasks so Taskiq can discover schedule labels declared on task functions.
from src.etl_service.presentation.taskiq import tasks  # noqa: F401

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
