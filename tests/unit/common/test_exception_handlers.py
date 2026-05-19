import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.common.presentation import register_exception_handlers


def test_unhandled_exception_handler_logs_exception(monkeypatch) -> None:
    calls: list[tuple[str, dict]] = []

    class FakeLogger:
        def exception(self, event: str, **kwargs) -> None:
            calls.append((event, kwargs))

    monkeypatch.setattr(
        structlog,
        "get_logger",
        lambda *_args, **_kwargs: FakeLogger(),
    )

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert calls == [
        (
            "Unhandled request exception",
            {
                "method": "GET",
                "path": "/boom",
                "exception_type": "RuntimeError",
            },
        )
    ]
