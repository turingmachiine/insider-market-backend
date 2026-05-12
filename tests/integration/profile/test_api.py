from uuid import UUID, uuid4

import httpx
import pytest

from src.common.application.security import create_service_token
from src.common.domain.security import Permission
from src.common.domain.service_auth import (
    PROFILE_BALANCE_WRITE_SCOPE,
    PROFILE_SERVICE_AUDIENCE,
    SERVICE_AUTHORIZATION_HEADER,
)
from src.profile_service.core.config import settings


@pytest.mark.asyncio
async def test_profile_balance_activity_and_achievement_flow(
    profile_client: httpx.AsyncClient,
    authenticated_user_id: UUID,
) -> None:
    user_id = str(authenticated_user_id)

    profile_response = await profile_client.post(
        "/api/v1/profiles",
        json={
            "user_id": user_id,
            "display_name": "Scout",
            "favorite_club": "Spartak",
            "initial_balance": 1200.0,
        },
    )
    assert profile_response.status_code == 201
    profile = profile_response.json()
    assert profile["balance"] == pytest.approx(1200.0)
    assert profile["available_balance"] == pytest.approx(1200.0)

    reserve_response = await profile_client.post(
        f"/api/v1/profiles/{user_id}/balance/transactions",
        json={
            "transaction_type": "reserve",
            "amount": 200.0,
            "source": "market.bet",
            "idempotency_key": "bet-1",
        },
    )
    assert reserve_response.status_code == 201
    assert reserve_response.json()["reserved_after"] == pytest.approx(200.0)

    balance_response = await profile_client.get(f"/api/v1/profiles/{user_id}/balance")
    assert balance_response.status_code == 200
    assert balance_response.json()["available_balance"] == pytest.approx(1000.0)

    activity_response = await profile_client.get(f"/api/v1/profiles/{user_id}/activity")
    assert activity_response.status_code == 200
    activity_types = [
        item["activity_type"] for item in activity_response.json()["items"]
    ]
    assert "profile_created" in activity_types
    assert "balance_changed" in activity_types

    achievement_response = await profile_client.post(
        "/api/v1/achievements",
        json={
            "code": "first_bet",
            "name": "First Bet",
            "description": "Placed a first market bet.",
        },
    )
    assert achievement_response.status_code == 201

    award_response = await profile_client.post(
        f"/api/v1/profiles/{user_id}/achievements",
        json={"achievement_code": "first_bet"},
    )
    assert award_response.status_code == 201
    assert award_response.json()["achievement"]["code"] == "first_bet"


@pytest.mark.asyncio
async def test_balance_operation_requires_profile(
    profile_client: httpx.AsyncClient,
    authenticated_user_id: UUID,
) -> None:
    response = await profile_client.post(
        f"/api/v1/profiles/{authenticated_user_id}/balance/transactions",
        json={
            "transaction_type": "debit",
            "amount": 100.0,
            "source": "market.bet",
        },
    )

    assert response.status_code == 404


async def test_internal_balance_operation_requires_service_auth(
    profile_client: httpx.AsyncClient,
    authenticated_user_id: UUID,
) -> None:
    create_response = await profile_client.post(
        "/api/v1/profiles",
        json={
            "user_id": str(UUID("00000000-0000-0000-0000-000000000002")),
            "display_name": "Internal Reward Target",
            "initial_balance": 100.0,
        },
    )
    assert create_response.status_code == 201

    url = f"/api/v1/internal/profiles/{authenticated_user_id}/balance/transactions"
    payload = {
        "transaction_type": "credit",
        "amount": "25.00",
        "source": "rating.achievement_reward",
        "idempotency_key": "reward-integration-1",
    }

    user_token_response = await profile_client.post(url, json=payload)
    assert user_token_response.status_code == 401

    service_token = create_service_token(
        PROFILE_SERVICE_AUDIENCE,
        settings,
        [PROFILE_BALANCE_WRITE_SCOPE],
    )
    service_response = await profile_client.post(
        url,
        headers={SERVICE_AUTHORIZATION_HEADER: f"Bearer {service_token}"},
        json=payload,
    )
    assert service_response.status_code == 201
    assert service_response.json()["amount"] == pytest.approx(25.0)


@pytest.mark.asyncio
async def test_create_profile_ignores_spoofed_user_id(
    profile_client: httpx.AsyncClient,
    authenticated_user_id: UUID,
) -> None:
    spoofed_user_id = str(uuid4())

    response = await profile_client.post(
        "/api/v1/profiles",
        json={
            "user_id": spoofed_user_id,
            "display_name": "Scout",
            "initial_balance": 1000.0,
        },
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == str(authenticated_user_id)


@pytest.mark.asyncio
async def test_user_cannot_read_another_users_profile_without_read_any(
    profile_client: httpx.AsyncClient,
    token_factory,
) -> None:
    owner_id = uuid4()
    reader_id = uuid4()
    profile_client.headers["Authorization"] = f"Bearer {token_factory(owner_id)}"

    response = await profile_client.post(
        "/api/v1/profiles",
        json={"user_id": str(owner_id), "display_name": "Private"},
    )
    assert response.status_code == 201

    token = token_factory(
        reader_id,
        permissions=[Permission.PROFILE_READ, Permission.PROFILE_WRITE],
    )
    profile_client.headers["Authorization"] = f"Bearer {token}"
    response = await profile_client.get(f"/api/v1/profiles/{owner_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_read_any_permission_allows_reading_another_users_profile(
    profile_client: httpx.AsyncClient,
    token_factory,
) -> None:
    owner_id = uuid4()
    reader_id = uuid4()
    profile_client.headers["Authorization"] = f"Bearer {token_factory(owner_id)}"

    response = await profile_client.post(
        "/api/v1/profiles",
        json={"user_id": str(owner_id), "display_name": "Audited"},
    )
    assert response.status_code == 201

    token = token_factory(
        reader_id,
        permissions=[Permission.PROFILE_READ, Permission.PROFILE_READ_ANY],
    )
    profile_client.headers["Authorization"] = f"Bearer {token}"
    response = await profile_client.get(f"/api/v1/profiles/{owner_id}")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(owner_id)


@pytest.mark.asyncio
async def test_user_cannot_update_another_users_profile(
    profile_client: httpx.AsyncClient,
    token_factory,
) -> None:
    owner_id = uuid4()
    attacker_id = uuid4()
    profile_client.headers["Authorization"] = f"Bearer {token_factory(owner_id)}"

    response = await profile_client.post(
        "/api/v1/profiles",
        json={"user_id": str(owner_id), "display_name": "Owner"},
    )
    assert response.status_code == 201

    profile_client.headers["Authorization"] = f"Bearer {token_factory(attacker_id)}"
    response = await profile_client.patch(
        f"/api/v1/profiles/{owner_id}",
        json={"display_name": "Compromised"},
    )

    assert response.status_code == 403
