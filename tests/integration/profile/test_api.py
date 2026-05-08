from uuid import uuid4

import httpx
import pytest


@pytest.mark.asyncio
async def test_profile_balance_activity_and_achievement_flow(
    profile_client: httpx.AsyncClient,
) -> None:
    user_id = str(uuid4())

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
    assert profile["balance"] == 1200.0
    assert profile["available_balance"] == 1200.0

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
    assert reserve_response.json()["reserved_after"] == 200.0

    balance_response = await profile_client.get(f"/api/v1/profiles/{user_id}/balance")
    assert balance_response.status_code == 200
    assert balance_response.json()["available_balance"] == 1000.0

    activity_response = await profile_client.get(f"/api/v1/profiles/{user_id}/activity")
    assert activity_response.status_code == 200
    activity_types = [
        item["activity_type"] for item in activity_response.json()["items"]
    ]
    assert "profile_created" in activity_types
    assert "balance_changed" in activity_types

    achievement_response = await profile_client.post(
        "/api/v1/profiles/-/achievements",
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
) -> None:
    response = await profile_client.post(
        f"/api/v1/profiles/{uuid4()}/balance/transactions",
        json={
            "transaction_type": "debit",
            "amount": 100.0,
            "source": "market.bet",
        },
    )

    assert response.status_code == 404
