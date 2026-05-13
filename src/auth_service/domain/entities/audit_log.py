from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.auth_service.core.utils.datetime_utils import utc_now


class AuditAction(StrEnum):
    REGISTER = "register"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET = "password_reset"
    USER_STATUS_UPDATE = "user_status_update"
    ROLE_ASSIGNMENT = "role_assignment"
    ROLE_REVOCATION = "role_revocation"
    ROLE_CREATE = "role_create"
    ROLE_PERMISSIONS_UPDATE = "role_permissions_update"
    PERMISSION_CREATE = "permission_create"
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
