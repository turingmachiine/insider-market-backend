import pytest

from src.common.infrastructure.taskiq import YamlJobComposer, YamlScheduleSource


def test_yaml_job_composer_reads_jobs(tmp_path) -> None:
    config_path = tmp_path / "jobs.yml"
    config_path.write_text(
        "\n".join(
            [
                "jobs:",
                "  - schedule_id: example_job",
                "    task_name: package.module:task",
                "    cron: '*/5 * * * *'",
                "    labels:",
                "      queue: default",
            ],
        ),
        encoding="utf-8",
    )

    jobs = YamlJobComposer(config_path).compose()

    assert len(jobs) == 1
    assert jobs[0].schedule_id == "example_job"
    assert jobs[0].task_name == "package.module:task"
    assert jobs[0].cron == "*/5 * * * *"
    assert jobs[0].labels == {"queue": "default"}


def test_yaml_job_composer_requires_single_trigger(tmp_path) -> None:
    config_path = tmp_path / "jobs.yml"
    config_path.write_text(
        "\n".join(
            [
                "jobs:",
                "  - schedule_id: broken_job",
                "    task_name: package.module:task",
                "    cron: '*/5 * * * *'",
                "    interval: 60",
            ],
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exactly one trigger"):
        YamlJobComposer(config_path).compose()


@pytest.mark.asyncio
async def test_yaml_schedule_source_exposes_taskiq_schedules(tmp_path) -> None:
    config_path = tmp_path / "jobs.yml"
    config_path.write_text(
        "\n".join(
            [
                "jobs:",
                "  - schedule_id: example_job",
                "    task_name: package.module:task",
                "    cron: '*/5 * * * *'",
            ],
        ),
        encoding="utf-8",
    )
    source = YamlScheduleSource(YamlJobComposer(config_path))

    await source.startup()

    schedules = await source.get_schedules()
    assert len(schedules) == 1
    assert schedules[0].schedule_id == "example_job"
    assert schedules[0].task_name == "package.module:task"
    assert schedules[0].cron == "*/5 * * * *"
