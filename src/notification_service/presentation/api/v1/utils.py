from uuid import UUID

from fastapi import HTTPException, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.presentation.utils import can_access_user_resource
from src.notification_service.application.constants import (
    NOTIFICATION_ACCESS_DENIED_DETAIL,
)
from src.notification_service.domain.entities import NotificationEvent


def subscription_user_id(
    user_context: UserContext,
    requested_user_id: UUID | None,
) -> UUID | None:
    if requested_user_id is None:
        return None
    if can_access_user_resource(
        user_context, requested_user_id, Permission.NOTIFICATION_READ_ANY
    ):
        return requested_user_id
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=NOTIFICATION_ACCESS_DENIED_DETAIL,
    )


def notification_event_payload(event: NotificationEvent) -> dict[str, object]:
    return {
        "id": str(event.id),
        "topic": event.topic.value,
        "event_type": event.event_type,
        "payload": event.payload,
        "user_id": str(event.user_id) if event.user_id else None,
        "created_at": event.created_at.isoformat(),
    }
