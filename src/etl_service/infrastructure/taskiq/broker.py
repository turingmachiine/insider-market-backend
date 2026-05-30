from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import ListQueueBroker

from src.etl_service.core.config import get_settings
from src.etl_service.infrastructure.di.container_factory import create_container

settings = get_settings()

broker = ListQueueBroker(
    url=settings.TASKIQ_REDIS_URL,
    queue_name=settings.TASKIQ_QUEUE_NAME,
)

container = create_container(settings)
setup_dishka(container=container, broker=broker)

# Import task handlers for worker processes started from this broker module.
from src.etl_service.presentation.taskiq import tasks  # noqa: E402,F401
