import logging
import queue
import sys
from logging.handlers import QueueHandler, QueueListener
from typing import Any, cast

import structlog
from structlog.typing import EventDict, Processor, WrappedLogger

from src.common.logging.handlers import RedisListLogHandler

_listener: QueueListener | None = None


class RawQueueHandler(QueueHandler):
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        return logging.makeLogRecord(record.__dict__.copy())


class PlainTextRenderer:
    def __call__(
        self,
        _: WrappedLogger,
        __: str,
        event_dict: EventDict,
    ) -> str:
        timestamp = event_dict.get("timestamp", "")
        level = str(event_dict.get("level", "")).upper()
        event = event_dict.get("event", "")
        return f"{timestamp} - {level} - {event}"


def _add_required_fields(
    _: WrappedLogger,
    __: str,
    event_dict: EventDict,
) -> EventDict:
    event_dict.setdefault("request_id", None)
    event_dict.setdefault("user_id", None)
    return event_dict


def _add_service_name(service_name: str) -> Processor:
    def processor(
        _: WrappedLogger,
        __: str,
        event_dict: EventDict,
    ) -> EventDict:
        event_dict["service"] = service_name
        return event_dict

    return processor


def setup_logging(
    *,
    service_name: str,
    json_logs: bool = True,
    log_level: str = "INFO",
    broker_url: str | None = None,
    broker_key: str = "logs:football",
    capture_warnings: bool | None = None,
) -> None:
    shutdown_logging()

    level = getattr(logging, log_level.upper(), logging.INFO)
    timestamper = structlog.processors.TimeStamper(
        fmt="iso",
        utc=True,
        key="timestamp",
    )
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _add_service_name(service_name),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        _add_required_fields,
        structlog.processors.EventRenamer("event"),
    ]

    stdout_renderer: Any
    if json_logs:
        stdout_renderer = PlainTextRenderer()
    else:
        stdout_renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    stdout_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            _add_service_name(service_name),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            timestamper,
            _add_required_fields,
            structlog.processors.EventRenamer("event"),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            stdout_renderer,
        ],
    )
    broker_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            _add_service_name(service_name),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            timestamper,
            _add_required_fields,
            structlog.processors.EventRenamer("event"),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_formatter)

    handlers: list[logging.Handler] = [stdout_handler]
    if broker_url:
        log_queue: queue.Queue[logging.LogRecord] = queue.Queue(-1)
        queue_handler = RawQueueHandler(log_queue)
        handlers.append(queue_handler)
        redis_handler = RedisListLogHandler(broker_url, broker_key)
        redis_handler.setFormatter(broker_formatter)
        global _listener
        _listener = QueueListener(log_queue, redis_handler, respect_handler_level=True)
        _listener.start()

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    for handler in handlers:
        handler.setLevel(level)
        root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(level)

    if capture_warnings is None:
        capture_warnings = "pytest" not in sys.modules
    logging.captureWarnings(capture_warnings)
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.handlers.clear()
    warnings_logger.propagate = capture_warnings

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service=service_name)


def shutdown_logging() -> None:
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None
    logging.captureWarnings(False)
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.handlers.clear()
    warnings_logger.propagate = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
