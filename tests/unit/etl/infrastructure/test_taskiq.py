import pytest
from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker

from src.common.infrastructure.taskiq import YamlScheduleSource
from src.etl_service.infrastructure.taskiq.broker import broker
from src.etl_service.infrastructure.taskiq.scheduler import scheduler
from src.etl_service.presentation.taskiq.tasks import (
    import_raw_publications_task,
    normalize_rumors_task,
)


def test_taskiq_broker_and_scheduler_are_configured() -> None:
    assert isinstance(broker, ListQueueBroker)
    assert isinstance(scheduler, TaskiqScheduler)
    assert isinstance(scheduler.sources[0], YamlScheduleSource)


def test_taskiq_tasks_do_not_define_inline_schedules() -> None:
    assert "schedule" not in import_raw_publications_task.labels
    assert "schedule" not in normalize_rumors_task.labels


def test_taskiq_broker_registers_worker_tasks() -> None:
    task_names = broker.get_all_tasks()

    assert (
        "src.etl_service.presentation.taskiq.tasks:import_raw_publications_task"
        in task_names
    )
    assert (
        "src.etl_service.presentation.taskiq.tasks:normalize_rumors_task" in task_names
    )


@pytest.mark.asyncio
async def test_yaml_scheduler_config_defines_cron_schedules() -> None:
    source = scheduler.sources[0]

    await source.startup()

    schedules = {
        schedule.schedule_id: schedule for schedule in await source.get_schedules()
    }
    assert schedules["import_raw_publications"].cron == "*/30 * * * *"
    assert schedules["normalize_rumors"].cron == "*/15 * * * *"
