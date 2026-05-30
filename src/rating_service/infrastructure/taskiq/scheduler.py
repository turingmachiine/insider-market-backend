from pathlib import Path

from src.common.infrastructure.taskiq import TaskiqSchedulerDriver, YamlJobComposer
from src.rating_service.core.config import get_settings
from src.rating_service.infrastructure.taskiq.broker import broker

# Import tasks so Taskiq registers task names referenced from the YAML config.
from src.rating_service.presentation.taskiq import tasks  # noqa: F401

settings = get_settings()
config_path = Path(settings.TASKIQ_JOBS_CONFIG_PATH)
composer = YamlJobComposer(config_path)
scheduler = TaskiqSchedulerDriver(broker=broker, composer=composer).create_scheduler()
