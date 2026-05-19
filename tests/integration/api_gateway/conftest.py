"""API gateway fixtures and test helpers."""

from collections import defaultdict
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import AnyHttpUrl
from testcontainers.redis import AsyncRedisContainer

from src.api_gateway.config import GatewaySettings
from src.api_gateway.main import create_app
from src.common.application.security import encode_jwt


@dataclass
class GatewayClientContext:
    client: httpx.AsyncClient
    calls: defaultdict[str, int]
    upstream_requests: list[httpx.Request]
    redis_client: object

    def __iter__(self):
        yield self.client
        yield self.calls
        yield self.upstream_requests
        yield self.redis_client


@dataclass
class ManagedGatewayClient:
    client: httpx.AsyncClient
    upstream_client: httpx.AsyncClient
    calls: defaultdict[str, int]
    redis_client: object

    async def close(self) -> None:
        await self.client.aclose()
        await self.upstream_client.aclose()

    def __iter__(self):
        yield self.client
        yield self.upstream_client
        yield self.calls
        yield self.redis_client


@pytest.fixture(scope="session")
def redis_container() -> Generator[AsyncRedisContainer, None, None]:
    with AsyncRedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture
def gateway_settings() -> GatewaySettings:
    return GatewaySettings(
        SERVICE_NSI_URL=AnyHttpUrl(url="http://nsi.test"),
        SERVICE_AUTH_URL=AnyHttpUrl(url="http://auth.test"),
        SERVICE_RUMOR_URL=AnyHttpUrl(url="http://rumor.test"),
        SERVICE_EVENT_URL=AnyHttpUrl(url="http://event.test"),
        SERVICE_MARKET_URL=AnyHttpUrl(url="http://market.test"),
        REDIS_URL="redis://redis.test:6379/0",
        RATE_LIMIT="100/minute",
        SENSITIVE_RATE_LIMIT="10/minute",
        WEBSOCKET_RATE_LIMIT="20/minute",
        RATE_LIMIT_BY_JWT=True,
        CACHE_TTL_SECONDS=30,
        CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"],
    )


def make_token(user_id: str, secret: str) -> str:
    return encode_jwt(
        {
            "sub": user_id,
            "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
        },
        secret,
        "HS256",
    )


def gateway_upstream_handler(
    calls: defaultdict[str, int],
    upstream_requests: list[httpx.Request],
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        upstream_requests.append(request)
        key = f"{request.url.host}{request.url.path}"
        calls[key] += 1
        if request.url.path == "/unavailable":
            raise httpx.ConnectError("service unavailable", request=request)
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200,
                json={
                    "openapi": "3.1.0",
                    "info": {"title": key, "version": "1.0.0"},
                    "tags": [{"name": "Health"}],
                    "paths": {
                        "/health": {
                            "get": {
                                "tags": ["Health"],
                                "operationId": "health_check",
                                "responses": {
                                    "200": {
                                        "description": "OK",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "$ref": (
                                                        "#/components/schemas/"
                                                        "HealthResponse"
                                                    )
                                                }
                                            }
                                        },
                                    }
                                },
                            }
                        }
                    },
                    "components": {
                        "schemas": {
                            "HealthResponse": {
                                "type": "object",
                                "properties": {"status": {"type": "string"}},
                            }
                        }
                    },
                },
            )
        return httpx.Response(
            200,
            json={
                "host": request.url.host,
                "path": request.url.path,
                "query": request.url.query.decode(),
                "body": request.content.decode(),
                "authorization": request.headers.get("authorization"),
                "x_forwarded_for": request.headers.get("x-forwarded-for"),
            },
        )

    return httpx.MockTransport(handler)


@pytest.fixture
async def gateway_client(
    gateway_settings: GatewaySettings,
    redis_container: AsyncRedisContainer,
) -> AsyncGenerator[GatewayClientContext, None]:
    calls: defaultdict[str, int] = defaultdict(int)
    upstream_requests: list[httpx.Request] = []
    upstream_client = httpx.AsyncClient(
        transport=gateway_upstream_handler(calls, upstream_requests)
    )
    redis_client = await redis_container.get_async_client()
    app = create_app(
        gateway_settings,
        redis_client=redis_client,
        http_client=upstream_client,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://gateway.test",
    ) as client:
        yield GatewayClientContext(client, calls, upstream_requests, redis_client)
    await upstream_client.aclose()


async def make_gateway_client(
    settings: GatewaySettings,
    redis_container: AsyncRedisContainer,
) -> ManagedGatewayClient:
    calls: defaultdict[str, int] = defaultdict(int)

    def handler(request: httpx.Request) -> httpx.Response:
        calls[f"{request.url.host}{request.url.path}"] += 1
        return httpx.Response(200, json={"path": request.url.path})

    upstream_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    redis_client = await redis_container.get_async_client()
    app = create_app(settings, redis_client=redis_client, http_client=upstream_client)
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://gateway.test",
    )
    return ManagedGatewayClient(client, upstream_client, calls, redis_client)
