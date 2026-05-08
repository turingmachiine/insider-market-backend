from decimal import Decimal
from uuid import uuid4

import httpx
import pytest


@pytest.mark.asyncio
async def test_rating_event_profile_achievement_and_reward_flow(
    rating_client: httpx.AsyncClient,
) -> None:
    user_id = str(uuid4())

    event_response = await rating_client.post(
        "/api/v1/ratings/events",
        json={
            "user_id": user_id,
            "event_type": "prediction_settled",
            "is_successful": True,
            "stake": "100",
            "payout": "175",
            "idempotency_key": "prediction-1",
        },
    )
    assert event_response.status_code == 201
    assert event_response.json()["processed_at"] is not None

    profile_response = await rating_client.get(f"/api/v1/ratings/profiles/{user_id}")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["total_predictions"] == 1
    assert profile["correct_predictions"] == 1
    assert profile["rating"] > 1000

    achievement_response = await rating_client.get(
        f"/api/v1/ratings/profiles/{user_id}/achievements"
    )
    assert achievement_response.status_code == 200
    achievements = achievement_response.json()["items"]
    assert achievements[0]["achievement_code"] == "first_prediction"
    assert Decimal(str(achievements[0]["reward_amount"])) == Decimal("25.0")

    reward_response = await rating_client.get("/api/v1/ratings/rewards/pending")
    assert reward_response.status_code == 200
    assert reward_response.json()["items"][0]["achievement_code"] == "first_prediction"


@pytest.mark.asyncio
async def test_rating_event_is_idempotent(rating_client: httpx.AsyncClient) -> None:
    user_id = str(uuid4())
    payload = {
        "user_id": user_id,
        "event_type": "daily_active",
        "idempotency_key": "daily-active-1",
    }

    first = await rating_client.post("/api/v1/ratings/events", json=payload)
    second = await rating_client.post("/api/v1/ratings/events", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
