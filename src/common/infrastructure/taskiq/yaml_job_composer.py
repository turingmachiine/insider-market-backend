from pathlib import Path
from typing import Any

import yaml

from src.common.application.scheduling import IJobComposer, ScheduledJob


class YamlJobComposer(IJobComposer):
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def compose(self) -> list[ScheduledJob]:
        payload = self._read_payload()
        jobs = payload.get("jobs", [])
        if not isinstance(jobs, list):
            msg = "Scheduler config field 'jobs' must be a list."
            raise ValueError(msg)

        return [self._compose_job(raw_job) for raw_job in jobs]

    def _read_payload(self) -> dict[str, Any]:
        if not self.config_path.exists():
            msg = f"Scheduler config does not exist: {self.config_path}"
            raise FileNotFoundError(msg)

        payload = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            msg = "Scheduler config root must be a mapping."
            raise ValueError(msg)
        return payload

    def _compose_job(self, raw_job: Any) -> ScheduledJob:
        if not isinstance(raw_job, dict):
            msg = "Scheduler job config must be a mapping."
            raise ValueError(msg)

        required_fields = ("schedule_id", "task_name")
        missing_fields = [field for field in required_fields if not raw_job.get(field)]
        if missing_fields:
            msg = "Scheduler job is missing fields: " + ", ".join(missing_fields)
            raise ValueError(msg)

        self._validate_trigger(raw_job)
        return ScheduledJob(
            task_name=raw_job["task_name"],
            schedule_id=raw_job["schedule_id"],
            labels=dict(raw_job.get("labels") or {}),
            args=list(raw_job.get("args") or []),
            kwargs=dict(raw_job.get("kwargs") or {}),
            task_id=raw_job.get("task_id"),
            cron=raw_job.get("cron"),
            cron_offset=raw_job.get("cron_offset"),
            time=raw_job.get("time"),
            interval=raw_job.get("interval"),
        )

    def _validate_trigger(self, raw_job: dict[str, Any]) -> None:
        triggers = [name for name in ("cron", "interval", "time") if raw_job.get(name)]
        if len(triggers) != 1:
            schedule_id = raw_job.get("schedule_id", "<unknown>")
            msg = (
                f"Scheduler job '{schedule_id}' must define exactly one trigger: "
                "cron, interval, or time."
            )
            raise ValueError(msg)
