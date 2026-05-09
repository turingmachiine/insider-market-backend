from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.admin_service.domain.entities import AdminActionType


@dataclass(frozen=True)
class HealthStatusDTO:
    service: str
    status: str
    version: str | None = None


@dataclass(frozen=True)
class EventModerationQueueDTO:
    items: list[dict]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class UserListDTO:
    items: list[UserSummaryDTO]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class EventModerationCommandDTO:
    notes: str | None = None
    resolved_by_user_id: UUID | None = None
    resolution: str | None = None


@dataclass(frozen=True)
class UserSummaryDTO:
    id: UUID
    email: str
    is_active: bool
    roles: list[str]
    permissions: list[str]
    created_at: datetime | None


@dataclass(frozen=True)
class UserStatusUpdateDTO:
    is_active: bool


@dataclass(frozen=True)
class UserRoleGrantDTO:
    role_name: str
    permissions: list[str]


@dataclass(frozen=True)
class SavedFilterCreateDTO:
    actor_user_id: UUID
    name: str
    scope: str
    criteria: dict


@dataclass(frozen=True)
class SavedFilterDTO:
    id: UUID
    actor_user_id: UUID
    name: str
    scope: str
    criteria: dict
    created_at: datetime


@dataclass(frozen=True)
class SavedFilterListDTO:
    items: list[SavedFilterDTO]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class AdminActionDTO:
    id: UUID
    action_type: AdminActionType
    entity_type: str
    entity_id: str
    summary: str
    actor_user_id: UUID | None
    payload: dict | None
    created_at: datetime


@dataclass(frozen=True)
class AdminActionListDTO:
    items: list[AdminActionDTO]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class ProfileSummaryDTO:
    profile: dict | None
    rating: dict | None
    permissions: list[str]


@dataclass(frozen=True)
class AdminDashboardDTO:
    services: list[HealthStatusDTO]
    event_moderation_queue_size: int
    users_total: int
    rating_leaderboard_size: int
    profiles_total: int
