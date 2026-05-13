from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.auth_service.core.utils.datetime_utils import utc_now


class AuditAction(StrEnum):
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"
    USER_STATUS_UPDATE = "user_status_update"
    ROLE_ASSIGNMENT = "role_assignment"
    TOKENS_REVOKE = "tokens_revoke"


@dataclass
class AuditLog:
    id: UUID
    action: AuditAction
    target_type: str
    target_id: str | None = None
    actor_user_id: UUID | None = None
    before: dict | None = None
    after: dict | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
