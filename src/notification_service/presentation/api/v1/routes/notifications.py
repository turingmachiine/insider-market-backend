import json
from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse

from src.common.application.security import TokenError, decode_access_token
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission
from src.notification_service.application.dto import (
    PublishNotificationDTO,
    SubscriptionDTO,
)
from src.notification_service.application.usecases import NotificationUseCases
from src.notification_service.core.config import settings
from src.notification_service.domain.entities import (
    NotificationEvent,
    NotificationTopic,
)
from src.notification_service.presentation.api.v1.schemas import (
    NotificationPublishRequest,
    NotificationPublishResponse,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])
DEFAULT_TOPICS = {
    NotificationTopic.MARKET,
    NotificationTopic.EVENT,
    NotificationTopic.RATING,
    NotificationTopic.SYSTEM,
}
TopicsQuery = Annotated[set[NotificationTopic], Query()]


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
@inject
async def publish_event(
    payload: NotificationPublishRequest,
    notification_use_cases: FromDishka[NotificationUseCases],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.NOTIFICATION_PUBLISH))
    ],
) -> NotificationPublishResponse:
    dto = PublishNotificationDTO(
        topic=payload.topic,
        event_type=payload.event_type,
        payload=payload.payload,
        user_id=payload.user_id,
    )
    result = await notification_use_cases.publish(dto)
    return NotificationPublishResponse(**result.__dict__)


@router.websocket("/ws")
@inject
async def websocket_notifications(
    websocket: WebSocket,
    notification_use_cases: FromDishka[NotificationUseCases],
    topics: TopicsQuery = DEFAULT_TOPICS,
    user_id: UUID | None = None,
) -> None:
    authorization = websocket.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        await websocket.close(code=4401)
        return

    try:
        payload = decode_access_token(token, settings)
    except TokenError:
        await websocket.close(code=4401)
        return

    permissions = set(payload.get("permissions", []))
    if Permission.NOTIFICATION_READ.value not in permissions:
        await websocket.close(code=4403)
        return

    subscription = SubscriptionDTO(topics=topics, user_id=user_id)
    await websocket.accept()
    try:
        async for event in notification_use_cases.subscribe(subscription):
            await websocket.send_json(_event_payload(event))
    except WebSocketDisconnect:
        return


@router.get("/stream")
@inject
async def stream_notifications(
    notification_use_cases: FromDishka[NotificationUseCases],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.NOTIFICATION_READ))
    ],
    topics: TopicsQuery = DEFAULT_TOPICS,
    user_id: UUID | None = None,
) -> StreamingResponse:
    subscription = SubscriptionDTO(topics=topics, user_id=user_id)

    async def stream() -> AsyncIterator[str]:
        async for event in notification_use_cases.subscribe(subscription):
            data = json.dumps(_event_payload(event), ensure_ascii=False, default=str)
            yield f"event: {event.event_type}\ndata: {data}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _event_payload(event: NotificationEvent) -> dict[str, object]:
    return {
        "id": str(event.id),
        "topic": event.topic.value,
        "event_type": event.event_type,
        "payload": event.payload,
        "user_id": str(event.user_id) if event.user_id else None,
        "created_at": event.created_at.isoformat(),
    }
