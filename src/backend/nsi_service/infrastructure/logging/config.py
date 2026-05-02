"""Настройка логирования приложения"""

from src.backend.common.logging import get_logger
from src.backend.common.logging import setup_logging as setup_common_logging

__all__ = ["get_logger", "setup_logging"]


def setup_logging(
    json_logs: bool = True,
    log_level: str = "INFO",
    broker_url: str | None = None,
    broker_key: str = "logs:football",
) -> None:
    """
    Настройка логирования с использованием structlog.

    Args:
        json_logs: Использовать JSON формат для логов
        log_level: Уровень логирования
    """
    setup_common_logging(
        service_name="nsi_service",
        json_logs=json_logs,
        log_level=log_level,
        broker_url=broker_url,
        broker_key=broker_key,
    )
