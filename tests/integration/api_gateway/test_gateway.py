import pytest
from pydantic import ValidationError
from testcontainers.redis import AsyncRedisContainer

from src.api_gateway.config import GatewaySettings
from tests.integration.api_gateway.conftest import make_gateway_client, make_token


def assert_security_headers(response) -> None:
    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["content-security-policy"] == (
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "img-src 'self' data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "connect-src 'self'"
    )
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )


@pytest.mark.asyncio
async def test_routes_request_to_expected_service(gateway_client) -> None:
    client, calls, _, _ = gateway_client
    response = await client.get(
        "/nsi/api/v1/players",
        headers={"Authorization": "Bearer token", "X-Forwarded-For": "1.2.3.4"},
    )

    assert response.status_code == 200
    assert_security_headers(response)
    assert response.json()["host"] == "nsi.test"
    assert response.json()["path"] == "/api/v1/players"
    assert response.json()["authorization"] == "Bearer token"
    assert response.json()["x_forwarded_for"] == "127.0.0.1"
    assert calls["nsi.test/api/v1/players"] == 1


@pytest.mark.asyncio
async def test_rumor_route_request_to_expected_service(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/rumor/api/v1/rumors?status=new")

    assert response.status_code == 200
    assert response.json()["host"] == "rumor.test"
    assert response.json()["path"] == "/api/v1/rumors"
    assert response.json()["query"] == "status=new"
    assert calls["rumor.test/api/v1/rumors"] == 1


@pytest.mark.asyncio
async def test_event_route_request_to_expected_service(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/event/api/v1/events?status=active")

    assert response.status_code == 200
    assert response.json()["host"] == "event.test"
    assert response.json()["path"] == "/api/v1/events"
    assert response.json()["query"] == "status=active"
    assert calls["event.test/api/v1/events"] == 1


@pytest.mark.asyncio
async def test_market_route_request_to_expected_service(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/market/api/v1/markets?status=active")

    assert response.status_code == 200
    assert response.json()["host"] == "market.test"
    assert response.json()["path"] == "/api/v1/markets"
    assert response.json()["query"] == "status=active"
    assert calls["market.test/api/v1/markets"] == 1


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
async def test_swagger_rumor_json_is_proxied(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/swagger/rumor/swagger.json")

    assert response.status_code == 200
    assert response.json()["openapi"] == "3.1.0"
    assert calls["rumor.test/openapi.json"] == 1


@pytest.mark.asyncio
async def test_swagger_event_json_is_proxied(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/swagger/event/swagger.json")

    assert response.status_code == 200
    assert response.json()["openapi"] == "3.1.0"
    assert calls["event.test/openapi.json"] == 1


@pytest.mark.asyncio
async def test_swagger_market_json_is_proxied(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/swagger/market/swagger.json")

    assert response.status_code == 200
    assert response.json()["openapi"] == "3.1.0"
    assert calls["market.test/openapi.json"] == 1


@pytest.mark.asyncio
async def test_docs_page_mentions_market_service(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/docs")

    assert response.status_code == 200
    assert "Market Service" in response.text
    assert "/swagger/market/swagger.json" in response.text
    assert "/market/api/v1/markets" in response.text


@pytest.mark.asyncio
async def test_aggregate_swagger_json_prefixes_service_paths(gateway_client) -> None:
    client, calls, _, _ = gateway_client

    response = await client.get("/swagger/swagger.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"] == "3.1.0"
    assert "/nsi/health" in schema["paths"]
    assert "/auth/health" in schema["paths"]
    assert "/rumor/health" in schema["paths"]
    assert "/event/health" in schema["paths"]
    assert "/market/health" in schema["paths"]
    assert "NsiHealthResponse" in schema["components"]["schemas"]
    assert "AuthHealthResponse" in schema["components"]["schemas"]
    assert "RumorHealthResponse" in schema["components"]["schemas"]
    assert "EventHealthResponse" in schema["components"]["schemas"]
    assert "MarketHealthResponse" in schema["components"]["schemas"]
    assert schema["tags"] == [{"name": "Health"}]
    assert schema["paths"]["/nsi/health"]["get"]["tags"] == ["Health"]
    assert schema["paths"]["/auth/health"]["get"]["tags"] == ["Health"]
    assert schema["paths"]["/rumor/health"]["get"]["tags"] == ["Health"]
    assert schema["paths"]["/event/health"]["get"]["tags"] == ["Health"]
    assert schema["paths"]["/market/health"]["get"]["tags"] == ["Health"]
    assert (
        schema["paths"]["/nsi/health"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/NsiHealthResponse"
    )
    assert schema["paths"]["/nsi/health"]["get"]["operationId"] == ("nsi_health_check")
    assert calls["nsi.test/openapi.json"] == 1
    assert calls["auth.test/openapi.json"] == 1
    assert calls["rumor.test/openapi.json"] == 1
    assert calls["event.test/openapi.json"] == 1
    assert calls["market.test/openapi.json"] == 1


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
async def test_event_post_mutation_invalidates_cached_url(gateway_client) -> None:
    client, calls, _, _ = gateway_client
    url = "/event/api/v1/events/42"

    assert (await client.get(url)).status_code == 200
    assert (await client.get(url)).status_code == 200
    assert calls["event.test/api/v1/events/42"] == 1

    assert (await client.post(f"{url}/approve")).status_code == 200
    assert (await client.get(url)).status_code == 200

    assert calls["event.test/api/v1/events/42"] == 2
    assert calls["event.test/api/v1/events/42/approve"] == 1


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
            int(
                (await redis_client.get("ratelimit:public:user:user-1:/auth/health"))
                or 0
            )
            == 2
        )
        assert (
            int(
                (await redis_client.get("ratelimit:public:user:user-2:/auth/health"))
                or 0
            )
            == 1
        )
    finally:
        await client.aclose()
        await upstream_client.aclose()


@pytest.mark.asyncio
async def test_sensitive_auth_route_uses_stricter_rate_limit(
    gateway_settings: GatewaySettings, redis_container: AsyncRedisContainer
) -> None:
    settings = gateway_settings.model_copy(
        update={"RATE_LIMIT": "100/minute", "SENSITIVE_RATE_LIMIT": "2/minute"}
    )
    client, upstream_client, calls, redis_client = await make_gateway_client(
        settings, redis_container
    )
    try:
        assert (await client.post("/auth/api/v1/login")).status_code == 200
        assert (await client.post("/auth/api/v1/login")).status_code == 200

        response = await client.post("/auth/api/v1/login")

        assert response.status_code == 429
        assert response.json() == {"detail": "Too Many Requests"}
        assert response.headers["retry-after"] == "60"
        assert calls["auth.test/api/v1/login"] == 2
        assert (
            int(
                (
                    await redis_client.get(
                        "ratelimit:sensitive:ip:127.0.0.1:/auth/api/v1/login"
                    )
                )
                or 0
            )
            == 3
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
    assert_security_headers(response)
    assert response.json() == {"detail": "Path traversal is not allowed"}
    assert calls == {}


@pytest.mark.asyncio
async def test_cors_preflight_uses_configured_origin(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": (
                "Authorization, Content-Type, X-Request-ID"
            ),
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-methods"] == (
        "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    )
    assert "Authorization" in response.headers["access-control-allow-headers"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]
    assert "X-Request-ID" in response.headers["access-control-allow-headers"]
    assert_security_headers(response)


@pytest.mark.asyncio
async def test_cors_simple_response_exposes_frontend_headers(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-expose-headers"] == (
        "X-Request-ID, Retry-After"
    )
    assert_security_headers(response)


@pytest.mark.asyncio
async def test_cors_preflight_rejects_unconfigured_origin(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.options(
        "/auth/login",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
    assert_security_headers(response)


def test_gateway_settings_reject_wildcard_cors_origin() -> None:
    with pytest.raises(ValidationError):
        GatewaySettings(CORS_ORIGINS=["*"])


@pytest.mark.asyncio
async def test_docs_page_returns_project_documentation(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/docs")

    assert response.status_code == 200
    assert '<link rel="stylesheet" href="/docs/assets/styles.css">' in response.text
    assert "Платформа прогнозов" in response.text
    assert "Как работает продукт" in response.text
    assert "Карта backend-сервисов" in response.text
    assert "prediction market" in response.text
    assert "/swagger/swagger.json" in response.text
    assert "/swagger-ui" in response.text
    assert "/swagger/auth/swagger.json" in response.text
    assert "/swagger/nsi/swagger.json" in response.text
    assert "/swagger/rumor/swagger.json" in response.text
    assert "/swagger/event/swagger.json" in response.text
    assert "/swagger-ui?url=/swagger/auth/swagger.json" in response.text
    assert "/swagger-ui?url=/swagger/nsi/swagger.json" in response.text
    assert "/swagger-ui?url=/swagger/rumor/swagger.json" in response.text
    assert "/swagger-ui?url=/swagger/event/swagger.json" in response.text


@pytest.mark.asyncio
async def test_legacy_swagger_index_redirects_to_docs(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/swagger/", follow_redirects=False)

    assert response.status_code == 308
    assert response.headers["location"] == "/docs"


@pytest.mark.asyncio
async def test_docs_stylesheet_is_served(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/docs/assets/styles.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert ".service-card" in response.text


@pytest.mark.asyncio
async def test_upstream_http_error_returns_bad_gateway(gateway_client) -> None:
    client, _, _, _ = gateway_client

    response = await client.get("/auth/unavailable")

    assert response.status_code == 502
    assert response.json() == {"detail": "Upstream service unavailable"}
