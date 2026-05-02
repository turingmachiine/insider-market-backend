from collections import defaultdict
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from jose import jwt
from pydantic import AnyHttpUrl
from testcontainers.redis import AsyncRedisContainer

from src.backend.api_gateway.config import GatewaySettings
from src.backend.api_gateway.main import create_app


@pytest.fixture
def gateway_settings() -> GatewaySettings:
    return GatewaySettings(
        SERVICE_NSI_URL=AnyHttpUrl(url="http://nsi.test"),
        SERVICE_AUTH_URL=AnyHttpUrl(url="http://auth.test"),
        REDIS_URL="redis://redis.test:6379/0",
        RATE_LIMIT="100/minute",
        RATE_LIMIT_BY_JWT=True,
        CACHE_TTL_SECONDS=30,
        CORS_ORIGINS=["http://localhost:3000"],
    )


@pytest.fixture
async def gateway_client(
    gateway_settings: GatewaySettings, redis_container: AsyncRedisContainer
):
    calls: defaultdict[str, int] = defaultdict(int)
    upstream_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        upstream_requests.append(request)
        key = f"{request.url.host}{request.url.path}"
        calls[key] += 1
        if request.url.path == "/unavailable":
            raise httpx.ConnectError("service unavailable", request=request)
        if request.url.path == "/openapi.json":
            return httpx.Response(
                200, json={"openapi": "3.1.0", "info": {"title": key}}
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

    upstream_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
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
        yield client, calls, upstream_requests, redis_client
    await upstream_client.aclose()


async def make_gateway_client(
    settings: GatewaySettings, redis_container: AsyncRedisContainer
):
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
    return client, upstream_client, calls, redis_client


def make_token(user_id: str, secret: str) -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )


@pytest.mark.asyncio
async def test_routes_request_to_expected_service(gateway_client) -> None:
    client, calls, _, _ = gateway_client
    response = await client.get(
        "/nsi/api/v1/players",
        headers={"Authorization": "Bearer token", "X-Forwarded-For": "1.2.3.4"},
    )

    assert response.status_code == 200
    assert response.json()["host"] == "nsi.test"
    assert response.json()["path"] == "/api/v1/players"
    assert response.json()["authorization"] == "Bearer token"
    assert response.json()["x_forwarded_for"] == "127.0.0.1"
    assert calls["nsi.test/api/v1/players"] == 1


@pytest.mark.asyncio
async def test_rate_limit_returns_429_on_101st_request(gateway_client) -> None:
    client, _, _, _ = gateway_client

    for _ in range(100):
        response = await client.get("/auth/health")
        assert response.status_code == 200

    response = await client.get("/auth/health")

    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}


@pytest.mark.asyncio
async def test_nsi_get_cache_serves_second_equal_request(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    first = await client.get("/nsi/api/v1/players?limit=10")
    second = await client.get("/nsi/api/v1/players?limit=10")

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["nsi.test/api/v1/players"] == 1


@pytest.mark.asyncio
async def test_swagger_auth_json_is_proxied(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/swagger/auth/swagger.json")

    assert response.status_code == 200
    assert response.json()["openapi"] == "3.1.0"
    assert calls["auth.test/openapi.json"] == 1


@pytest.mark.asyncio
async def test_query_string_and_body_are_forwarded(gateway_client) -> None:
    client, _, upstream_requests, _ = gateway_client

    response = await client.post(
        "/auth/login?next=/profile",
        content=b'{"email":"user@example.com"}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["query"] == "next=/profile"
    assert response.json()["body"] == '{"email":"user@example.com"}'
    assert upstream_requests[-1].headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_auth_service_get_requests_are_not_cached(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    first = await client.get("/auth/permissions/me")
    second = await client.get("/auth/permissions/me")

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls["auth.test/permissions/me"] == 2


@pytest.mark.asyncio
async def test_nsi_mutation_invalidates_cached_url(gateway_client) -> None:
    client, calls, _, _ = gateway_client
    url = "/nsi/api/v1/players/42?include_stats=true"

    assert (await client.get(url)).status_code == 200
    assert (await client.get(url)).status_code == 200
    assert calls["nsi.test/api/v1/players/42"] == 1

    assert (await client.put(url, json={"name": "Updated"})).status_code == 200
    assert (await client.get(url)).status_code == 200

    assert calls["nsi.test/api/v1/players/42"] == 3


@pytest.mark.asyncio
async def test_rate_limit_uses_jwt_subject_when_enabled(
    gateway_settings: GatewaySettings, redis_container: AsyncRedisContainer
) -> None:
    settings = gateway_settings.model_copy(update={"RATE_LIMIT": "1/minute"})
    client, upstream_client, _, redis_client = await make_gateway_client(
        settings, redis_container
    )
    try:
        user_1 = {
            "Authorization": f"Bearer {make_token('user-1', settings.JWT_SECRET)}"
        }
        user_2 = {
            "Authorization": f"Bearer {make_token('user-2', settings.JWT_SECRET)}"
        }

        assert (await client.get("/auth/health", headers=user_1)).status_code == 200
        assert (await client.get("/auth/health", headers=user_1)).status_code == 429
        assert (await client.get("/auth/health", headers=user_2)).status_code == 200

        assert (
            int((await redis_client.get("ratelimit:user:user-1:/auth/health")) or 0)
            == 2
        )
        assert (
            int((await redis_client.get("ratelimit:user:user-2:/auth/health")) or 0)
            == 1
        )
    finally:
        await client.aclose()
        await upstream_client.aclose()


@pytest.mark.asyncio
async def test_oversized_body_is_rejected_before_proxy(
    gateway_settings: GatewaySettings, redis_container: AsyncRedisContainer
) -> None:
    settings = gateway_settings.model_copy(update={"MAX_BODY_SIZE_MB": 0})
    client, upstream_client, calls, _ = await make_gateway_client(
        settings, redis_container
    )
    try:
        response = await client.post("/auth/login", content=b"x")

        assert response.status_code == 413
        assert response.json() == {"detail": "Request body is too large"}
        assert calls == {}
    finally:
        await client.aclose()
        await upstream_client.aclose()


@pytest.mark.asyncio
async def test_path_traversal_is_rejected_before_proxy(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/nsi/api/%2E%2E/health")

    assert response.status_code == 400
    assert response.json() == {"detail": "Path traversal is not allowed"}
    assert calls == {}


@pytest.mark.asyncio
async def test_cors_preflight_uses_configured_origin(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_swagger_index_returns_service_selector(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/swagger/")

    assert response.status_code == 200
    assert '<link rel="stylesheet" href="/swagger/assets/styles.css">' in response.text
    assert "Football analytics APIs from one entry point." in response.text
    assert "OpenAPI Gateway" in response.text
    assert "Gateway capabilities" in response.text
    assert "/swagger/auth/swagger.json" in response.text
    assert "/swagger/nsi/swagger.json" in response.text
    assert "/docs?url=/swagger/auth/swagger.json" in response.text
    assert "/docs?url=/swagger/nsi/swagger.json" in response.text


@pytest.mark.asyncio
async def test_swagger_stylesheet_is_served(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/swagger/assets/styles.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert ".service-card" in response.text


@pytest.mark.asyncio
async def test_upstream_http_error_returns_bad_gateway(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/auth/unavailable")

    assert response.status_code == 502
    assert response.json() == {"detail": "Upstream service unavailable"}
