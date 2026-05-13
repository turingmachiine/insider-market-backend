from types import SimpleNamespace

import pytest
from starlette.types import Message, Receive, Scope, Send

from src.api_gateway.middleware.rate_limit import (
    RateLimitMiddleware,
    WebSocketRateLimitMiddleware,
)


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def incr(self, key: str) -> int:  # NOSONAR(S7503)
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    async def expire(self, key: str, seconds: int) -> None:  # NOSONAR(S7503)
        self.expirations[key] = seconds


@pytest.mark.asyncio
async def test_websocket_rate_limit_closes_before_downstream_app() -> None:
    redis = FakeRedis()
    downstream_calls = 0
    sent_messages: list[dict[str, object]] = []

    async def downstream_app(scope, receive, send) -> None:  # NOSONAR(S7503)
        nonlocal downstream_calls
        downstream_calls += 1

    middleware = WebSocketRateLimitMiddleware(
        downstream_app,
        limit_per_minute=1,
        by_jwt=False,
    )
    scope = {
        "type": "websocket",
        "path": "/notification/api/v1/notifications/ws",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "app": SimpleNamespace(state=SimpleNamespace(redis=redis)),
    }

    async def receive() -> dict[str, object]:  # NOSONAR(S7503)
        return {"type": "websocket.connect"}

    async def send(message: Message) -> None:  # NOSONAR(S7503)
        sent_messages.append(dict(message))

    await middleware(scope, receive, send)
    await middleware(scope, receive, send)

    assert downstream_calls == 1
    assert sent_messages == [
        {
            "type": "websocket.close",
            "code": 4408,
            "reason": "Too Many Requests",
        }
    ]
    assert (
        redis.values[
            "ratelimit:websocket:ip:127.0.0.1:/notification/api/v1/notifications/ws"
        ]
        == 2
    )


def test_password_reset_routes_use_sensitive_rate_limit_policy() -> None:
    async def downstream_app(scope: Scope, receive: Receive, send: Send) -> None:
        """метод-заплатка для инициализации App"""
        pass

    middleware = RateLimitMiddleware(
        app=downstream_app,
        limit_per_minute=100,
        public_limit_per_minute=50,
        sensitive_limit_per_minute=2,
        by_jwt=False,
    )

    request_policy = middleware._policy_for(
        "POST",
        "/auth/api/v1/password/reset/request",
    )
    reset_policy = middleware._policy_for("POST", "/auth/api/v1/password/reset")

    assert request_policy.name == "sensitive"
    assert request_policy.limit_per_minute == 2
    assert reset_policy.name == "sensitive"
    assert reset_policy.limit_per_minute == 2
