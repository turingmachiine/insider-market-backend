from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.admin_service.domain.entities import AdminActionType


class HealthStatusResponse(BaseModel):
    service: str
    status: str
    version: str | None = None


class EventModerationQueueResponse(BaseModel):
    items: list[dict]
    total: int
    limit: int
    offset: int


class EventModerationCommandRequest(BaseModel):
    notes: str | None = None
    resolved_by_user_id: UUID | None = None
    resolution: str | None = None


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class UserRoleGrantRequest(BaseModel):
    role_name: str = Field(min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list)


class SavedFilterCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    scope: str = Field(min_length=1, max_length=120)
    criteria: dict


class UserSummaryResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    roles: list[str]
    permissions: list[str]
    created_at: datetime | None = None


class UserListResponse(BaseModel):
    items: list[UserSummaryResponse]
    total: int
    limit: int
    offset: int


class SavedFilterResponse(BaseModel):
    id: UUID
    actor_user_id: UUID
    name: str
    scope: str
    criteria: dict
    created_at: datetime


class SavedFilterListResponse(BaseModel):
    items: list[SavedFilterResponse]
    total: int
    limit: int
    offset: int


class AdminActionResponse(BaseModel):
    id: UUID
    action_type: AdminActionType
    entity_type: str
    entity_id: str
    summary: str
    actor_user_id: UUID | None
    payload: dict | None
    created_at: datetime


class AdminActionListResponse(BaseModel):
    items: list[AdminActionResponse]
    total: int
    limit: int
    offset: int


class AdminDashboardResponse(BaseModel):
    services: list[HealthStatusResponse]
    event_moderation_queue_size: int
    users_total: int
    rating_leaderboard_size: int
    profiles_total: int


class ProfileSummaryResponse(BaseModel):
    profile: dict | None
    rating: dict | None
    permissions: list[str]
