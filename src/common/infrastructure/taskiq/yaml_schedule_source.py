from taskiq.abc.broker import AsyncBroker
from taskiq.abc.schedule_source import ScheduleSource
from taskiq.scheduler.scheduled_task import ScheduledTask

from src.common.application.scheduling import IJobComposer, ScheduledJob


class YamlScheduleSource(ScheduleSource):
    def __init__(
        self, composer: IJobComposer, broker: AsyncBroker | None = None
    ) -> None:
        self.composer = composer
        self.broker = broker
        self.schedules: dict[str, ScheduledTask] = {}

    async def startup(self) -> None:
        jobs = self.composer.compose()
        self._validate_task_names(jobs)
        self.schedules = {job.schedule_id: self._to_scheduled_task(job) for job in jobs}
        await super().startup()

    async def get_schedules(self) -> list[ScheduledTask]:
        return list(self.schedules.values())

    def post_send(self, task: ScheduledTask) -> None:
        if task.cron or not task.time:
            return
        self.schedules.pop(task.schedule_id, None)

    def _to_scheduled_task(self, job: ScheduledJob) -> ScheduledTask:
        return ScheduledTask(
            task_name=job.task_name,
            labels=job.labels,
            args=job.args,
            kwargs=job.kwargs,
            task_id=job.task_id,
            schedule_id=job.schedule_id,
            cron=job.cron,
            cron_offset=job.cron_offset,
            time=job.time,
            interval=job.interval,
        )

    def _validate_task_names(self, jobs: list[ScheduledJob]) -> None:
        if self.broker is None:
            return

        registered_task_names = self.broker.get_all_tasks().keys()
        missing_task_names = [
            job.task_name for job in jobs if job.task_name not in registered_task_names
        ]
        if missing_task_names:
            msg = "Scheduler config references unknown task names: " + ", ".join(
                sorted(missing_task_names),
            )
            raise ValueError(msg)
