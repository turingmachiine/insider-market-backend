from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import ListQueueBroker

from src.rating_service.core.config import get_settings
from src.rating_service.infrastructure.db import setup_mapping
from src.rating_service.infrastructure.di import create_container

settings = get_settings()
setup_mapping()

broker = ListQueueBroker(
    url=settings.TASKIQ_REDIS_URL,
    queue_name=settings.TASKIQ_QUEUE_NAME,
)

container = create_container(settings, include_taskiq=True)
setup_dishka(container=container, broker=broker)

# Import task handlers for worker processes started from this broker module.
from src.rating_service.presentation.taskiq import tasks  # noqa: E402,F401
