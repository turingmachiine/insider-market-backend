from decimal import Decimal
from uuid import UUID

import httpx
import pytest
from pydantic import AnyHttpUrl

from src.common.application.security import decode_jwt
from src.common.domain.service_auth import SERVICE_AUTHORIZATION_HEADER
from src.rating_service.core.config import RatingSettings
from src.rating_service.infrastructure.clients.profile_balance_client import (
    ProfileBalanceClient,
)


@pytest.mark.asyncio
async def test_credit_reward_uses_internal_service_auth_endpoint() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(201, json={"id": "ok"})

    settings = RatingSettings(
        PROFILE_SERVICE_URL=AnyHttpUrl("http://profile.test"),
        SERVICE_JWT_SECRET="service-secret",
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ProfileBalanceClient("http://profile.test", http_client, settings)

        await client.credit_achievement_reward(
            user_id=UUID("00000000-0000-0000-0000-000000000001"),
            amount=Decimal("10"),
            achievement_code="first-win",
            idempotency_key="reward-1",
        )

    assert len(captured_requests) == 1
    captured_request = captured_requests[0]
    expected_path = (
        "/api/v1/internal/profiles/"
        "00000000-0000-0000-0000-000000000001"
        "/balance/transactions"
    )
    assert captured_request.url.path == expected_path
    service_authorization = captured_request.headers[SERVICE_AUTHORIZATION_HEADER]
    _, _, token = service_authorization.partition(" ")
    claims = decode_jwt(
        token, settings.SERVICE_JWT_SECRET, settings.SERVICE_JWT_ALGORITHM
    )
    assert claims["sub"] == "rating_service"
    assert claims["aud"] == "profile_service"
    assert claims["scopes"] == ["profile:balance:write"]
