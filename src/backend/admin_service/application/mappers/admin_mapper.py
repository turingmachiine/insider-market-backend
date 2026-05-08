from datetime import datetime
from uuid import UUID

from src.backend.admin_service.application.dto import (
    AdminActionDTO,
    AdminDashboardDTO,
    HealthStatusDTO,
    ProfileSummaryDTO,
    SavedFilterDTO,
    UserSummaryDTO,
)
from src.backend.admin_service.domain.entities import AdminAction, SavedFilter


class AdminMapper:
    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return None

    def health_to_dto(self, service: str, payload: dict) -> HealthStatusDTO:
        return HealthStatusDTO(
            service=service,
            status=str(payload.get("status", "unknown")),
            version=payload.get("version"),
        )

    def user_to_dto(self, payload: dict) -> UserSummaryDTO:
        return UserSummaryDTO(
            id=UUID(str(payload["id"])),
            email=payload["email"],
            is_active=bool(payload["is_active"]),
            roles=list(payload.get("roles", [])),
            permissions=list(payload.get("permissions", [])),
            created_at=self._parse_datetime(payload.get("created_at")),
        )

    def filter_to_dto(self, saved_filter: SavedFilter) -> SavedFilterDTO:
        return SavedFilterDTO(
            id=saved_filter.id,
            actor_user_id=saved_filter.actor_user_id,
            name=saved_filter.name,
            scope=saved_filter.scope,
            criteria=saved_filter.criteria,
            created_at=saved_filter.created_at,
        )

    def action_to_dto(self, action: AdminAction) -> AdminActionDTO:
        return AdminActionDTO(
            id=action.id,
            action_type=action.action_type,
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            summary=action.summary,
            actor_user_id=action.actor_user_id,
            payload=action.payload,
            created_at=action.created_at,
        )

    @staticmethod
    def profile_summary_to_dto(payload: dict) -> ProfileSummaryDTO:
        return ProfileSummaryDTO(
            profile=payload.get("profile"),
            rating=payload.get("rating"),
            permissions=list(payload.get("permissions", [])),
        )

    @staticmethod
    def dashboard_to_dto(
        services: list[HealthStatusDTO],
        event_queue_size: int,
        users_total: int,
        rating_leaderboard_size: int,
        profiles_total: int,
    ) -> AdminDashboardDTO:
        return AdminDashboardDTO(
            services=services,
            event_moderation_queue_size=event_queue_size,
            users_total=users_total,
            rating_leaderboard_size=rating_leaderboard_size,
            profiles_total=profiles_total,
        )
