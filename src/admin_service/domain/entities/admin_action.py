from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.admin_service.core.utils.datetime_utils import utc_now


class AdminActionType(StrEnum):
    EVENT_APPROVE = "event_approve"
    EVENT_REJECT = "event_reject"
    EVENT_RESOLVE = "event_resolve"
    EVENT_CANCEL = "event_cancel"
    EVENT_SUBMIT = "event_submit"
    USER_STATUS = "user_status"
    USER_ROLE = "user_role"
    FILTER_CREATE = "filter_create"


@dataclass
class AdminAction:
    id: UUID
    action_type: AdminActionType
    entity_type: str
    entity_id: str
    summary: str
    actor_user_id: UUID | None = None
    payload: dict | None = None
    before: dict | None = None
    after: dict | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
