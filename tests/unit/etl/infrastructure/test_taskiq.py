from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker

from src.etl_service.infrastructure.taskiq.broker import broker
from src.etl_service.infrastructure.taskiq.scheduler import scheduler
from src.etl_service.presentation.taskiq.tasks import (
    import_raw_publications_task,
    normalize_rumors_task,
)


def test_taskiq_broker_and_scheduler_are_configured() -> None:
    assert isinstance(broker, ListQueueBroker)
    assert isinstance(scheduler, TaskiqScheduler)


def test_taskiq_tasks_have_cron_schedules() -> None:
    assert import_raw_publications_task.labels["schedule"][0]["schedule_id"] == (
        "import_raw_publications"
    )
    assert normalize_rumors_task.labels["schedule"][0]["schedule_id"] == (
        "normalize_rumors"
    )
