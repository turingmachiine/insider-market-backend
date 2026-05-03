import json
import logging
import warnings

import structlog

from src.backend.common.logging import setup_logging, shutdown_logging


def test_structlog_writes_formatted_stdout(capsys) -> None:
    setup_logging(service_name="test_service", json_logs=True, log_level="INFO")

    structlog.contextvars.bind_contextvars(
        request_id="request-1",
        user_id="user-1",
    )
    structlog.get_logger("test").info("test_event", answer=42)

    captured = capsys.readouterr()
    timestamp, level, message = captured.out.strip().split(" - ", 2)

    assert timestamp
    assert level == "INFO"
    assert message == "test_event"

    shutdown_logging()


def test_context_unbind_removes_value_from_next_broker_log(monkeypatch, capsys) -> None:
    records: list[tuple[str, str]] = []

    class FakeRedis:
        def rpush(self, key: str, value: str) -> None:
            records.append((key, value))

    monkeypatch.setattr(
        "src.backend.common.logging.handlers.redis.Redis.from_url",
        lambda *_, **__: FakeRedis(),
    )

    setup_logging(
        service_name="test_service",
        json_logs=True,
        log_level="INFO",
        broker_url="redis://example/0",
    )

    structlog.contextvars.bind_contextvars(request_id="request-1")
    structlog.contextvars.unbind_contextvars("request_id")
    structlog.get_logger("test").info("test_event")
    shutdown_logging()
    capsys.readouterr()

    payload = json.loads(records[0][1])

    assert payload["request_id"] is None


def test_stdlib_logging_uses_formatted_stdout(capsys) -> None:
    setup_logging(service_name="test_service", json_logs=True, log_level="INFO")

    logging.getLogger("test").info("stdlib_event", extra={"request_id": "request-1"})

    captured = capsys.readouterr()
    timestamp, level, message = captured.out.strip().split(" - ", 2)

    assert timestamp
    assert level == "INFO"
    assert message == "stdlib_event"

    shutdown_logging()


def test_setup_logging_does_not_route_warnings_to_stdout_under_pytest(capsys) -> None:
    setup_logging(service_name="test_service", json_logs=True, log_level="INFO")

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        warnings.warn("pytest_warning_noise", RuntimeWarning, stacklevel=1)

    captured = capsys.readouterr()

    assert "py.warnings" not in captured.out
    assert "pytest_warning_noise" not in captured.out

    shutdown_logging()


def test_broker_handler_receives_same_json_payload(monkeypatch, capsys) -> None:
    records: list[tuple[str, str]] = []

    class FakeRedis:
        def rpush(self, key: str, value: str) -> None:
            records.append((key, value))

    monkeypatch.setattr(
        "src.backend.common.logging.handlers.redis.Redis.from_url",
        lambda *_, **__: FakeRedis(),
    )

    setup_logging(
        service_name="test_service",
        json_logs=True,
        log_level="INFO",
        broker_url="redis://example/0",
        broker_key="logs:test",
    )
    structlog.get_logger("test").info("broker_event")
    shutdown_logging()
    capsys.readouterr()

    assert records
    key, raw_payload = records[0]
    payload = json.loads(raw_payload)
    assert key == "logs:test"
    assert payload["timestamp"]
    assert payload["service"] == "test_service"
    assert payload["level"] == "info"
    assert payload["event"] == "broker_event"
    assert payload["request_id"] is None
    assert payload["user_id"] is None
