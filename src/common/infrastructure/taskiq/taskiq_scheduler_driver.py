from taskiq import TaskiqScheduler
from taskiq.abc.broker import AsyncBroker

from src.common.application.scheduling import IJobComposer, ISchedulerDriver
from src.common.infrastructure.taskiq.yaml_schedule_source import YamlScheduleSource


class TaskiqSchedulerDriver(ISchedulerDriver):
    def __init__(self, broker: AsyncBroker, composer: IJobComposer) -> None:
        self.broker = broker
        self.composer = composer

    def create_scheduler(self) -> TaskiqScheduler:
        return TaskiqScheduler(
            broker=self.broker,
            sources=[YamlScheduleSource(composer=self.composer, broker=self.broker)],
        )
