from uuid import uuid4

import httpx

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.notification_service.presentation.api.v1.utils import subscription_user_id


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


async def test_stream_rejects_another_users_personal_notifications(
    notification_client: httpx.AsyncClient,
    token_factory,
) -> None:
    reader_id = uuid4()
    target_user_id = uuid4()
    token = token_factory(
        reader_id,
        permissions=[Permission.NOTIFICATION_READ.value],
    )
    notification_client.headers["Authorization"] = f"Bearer {token}"

    response = await notification_client.get(
        "/api/v1/notifications/stream",
        params={"user_id": str(target_user_id)},
    )

    assert response.status_code == 403


async def test_stream_allows_read_any_for_another_user() -> None:  # NOSONAR(S7503)
    reader_id = uuid4()
    target_user_id = uuid4()
    target_subscription_user_id = subscription_user_id(
        UserContext(
            user_id=reader_id,
            subject=str(reader_id),
            permissions=frozenset(
                [
                    Permission.NOTIFICATION_READ.value,
                    Permission.NOTIFICATION_READ_ANY.value,
                ]
            ),
        ),
        target_user_id,
    )

    assert target_subscription_user_id == target_user_id
