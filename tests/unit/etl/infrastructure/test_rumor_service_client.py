from datetime import UTC, datetime
from uuid import UUID

import httpx
import pytest

from src.common.application.security import decode_jwt
from src.common.domain.service_auth import SERVICE_AUTHORIZATION_HEADER
from src.etl_service.application.dto import CreateRawPublicationDTO
from src.etl_service.core.config import ETLSettings
from src.etl_service.infrastructure.clients import RumorServiceHttpClient


@pytest.mark.asyncio
async def test_create_publication_uses_internal_service_auth_endpoint() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(
            201,
            json={
                "id": "00000000-0000-0000-0000-000000000101",
                "source_id": "00000000-0000-0000-0000-000000000001",
                "text": "rumor text",
                "external_id": None,
                "url": None,
                "published_at": None,
                "collected_at": datetime.now(UTC).isoformat(),
                "payload": {},
            },
        )

    settings = ETLSettings(
        RUMOR_SERVICE_URL="http://rumor.test",
        SERVICE_JWT_SECRET="service-secret",
    )
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="http://rumor.test",
    ) as http_client:
        client = RumorServiceHttpClient(http_client, settings)

        await client.create_raw_publication(
            CreateRawPublicationDTO(
                source_id=UUID("00000000-0000-0000-0000-000000000001"),
                text="rumor text",
            )
        )

    assert len(captured_requests) == 1
    captured_request = captured_requests[0]
    assert captured_request.url.path == "/api/v1/internal/raw-publications"
    service_authorization = captured_request.headers[SERVICE_AUTHORIZATION_HEADER]
    _, _, token = service_authorization.partition(" ")
    claims = decode_jwt(
        token, settings.SERVICE_JWT_SECRET, settings.SERVICE_JWT_ALGORITHM
    )
    assert claims["sub"] == "etl_service"
    assert claims["aud"] == "rumor_service"
    assert claims["scopes"] == ["rumor:ingest"]
