from uuid import uuid4

import httpx


async def test_publish_notification_event(
    notification_client: httpx.AsyncClient,
) -> None:
    user_id = str(uuid4())

    response = await notification_client.post(
        "/api/v1/notifications/events",
        json={
            "topic": "market",
            "event_type": "market.odds_changed",
            "payload": {"market_id": "m-1", "yes_probability": 0.57},
            "user_id": user_id,
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["topic"] == "market"
    assert body["event_type"] == "market.odds_changed"
    assert body["payload"] == {"market_id": "m-1", "yes_probability": 0.57}
    assert body["user_id"] == user_id
    assert set(body["channels"]) == {
        "notifications.topic.market",
        f"notifications.user.{user_id}",
    }


async def test_publish_rejects_unknown_topic(
    notification_client: httpx.AsyncClient,
) -> None:
    response = await notification_client.post(
        "/api/v1/notifications/events",
        json={"topic": "unknown", "event_type": "x", "payload": {}},
    )

    assert response.status_code == 422
