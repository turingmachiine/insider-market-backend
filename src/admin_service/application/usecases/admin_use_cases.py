from uuid import UUID, uuid4

from src.admin_service.application.dto import (
    AdminActionListDTO,
    AdminDashboardDTO,
    EventModerationCommandDTO,
    EventModerationQueueDTO,
    HealthStatusDTO,
    ProfileSummaryDTO,
    RoleCreateDTO,
    RolePermissionsUpdateDTO,
    SavedFilterCreateDTO,
    SavedFilterDTO,
    SavedFilterListDTO,
    UserListDTO,
    UserRoleGrantDTO,
    UserStatusUpdateDTO,
    UserSummaryDTO,
)
from src.admin_service.application.mappers import AdminMapper
from src.admin_service.application.ports import AdminGatewayClient
from src.admin_service.domain.entities import AdminAction, AdminActionType, SavedFilter
from src.admin_service.domain.interfaces.repositories import (
    IAdminActionRepository,
    ISavedFilterRepository,
)
from src.common.application.decorators import transactional, use_case
from src.common.application.protocols import HasTransactionManager
from src.common.domain.interfaces import TransactionManager


@use_case
class AdminUseCases(HasTransactionManager):
    gateway_client: AdminGatewayClient
    action_repository: IAdminActionRepository
    filter_repository: ISavedFilterRepository
    mapper: AdminMapper
    transaction_manager: TransactionManager

    async def get_dashboard_overview(self) -> AdminDashboardDTO:
        services = [
            self.mapper.health_to_dto(name, await self.gateway_client.get_health(name))
            for name in [
                "nsi",
                "auth",
                "rumor",
                "event",
                "market",
                "notification",
                "profile",
                "rating",
            ]
        ]
        event_queue = await self.get_event_moderation_queue(limit=1, offset=0)
        users = await self.get_users(limit=1, offset=0)
        rating = await self.gateway_client.get_rating_leaderboard(limit=1)
        profiles = await self.gateway_client.list_profiles(limit=1, offset=0)
        return self.mapper.dashboard_to_dto(
            services=services,
            event_queue_size=event_queue.total,
            users_total=users.total,
            rating_leaderboard_size=int(
                rating.get("total", len(rating.get("items", [])))
            ),
            profiles_total=int(profiles.get("total", len(profiles.get("items", [])))),
        )

    async def get_system_health(self) -> list[HealthStatusDTO]:
        return [
            self.mapper.health_to_dto(name, await self.gateway_client.get_health(name))
            for name in [
                "nsi",
                "auth",
                "rumor",
                "event",
                "market",
                "notification",
                "profile",
                "rating",
            ]
        ]

    async def get_event_moderation_queue(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> EventModerationQueueDTO:
        result = await self.gateway_client.get_event_moderation_queue(
            limit=limit,
            offset=offset,
        )
        return EventModerationQueueDTO(
            items=list(result.get("items", [])),
            total=int(result.get("total", len(result.get("items", [])))),
            limit=limit,
            offset=offset,
        )

    @transactional()
    async def submit_event_for_moderation(
        self,
        event_id: UUID,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        result = await self.gateway_client.call_event_action(
            event_id,
            "submit-moderation",
        )
        await self._record_action(
            AdminActionType.EVENT_SUBMIT,
            "event",
            str(event_id),
            "Submitted event for moderation",
            result,
            actor_user_id=actor_user_id,
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def approve_event(
        self,
        event_id: UUID,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        result = await self.gateway_client.call_event_action(event_id, "approve")
        await self._record_action(
            AdminActionType.EVENT_APPROVE,
            "event",
            str(event_id),
            "Approved event",
            result,
            actor_user_id=actor_user_id,
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def reject_event(
        self,
        event_id: UUID,
        notes: str | None = None,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        request_payload = {"notes": notes} if notes else {}
        result = await self.gateway_client.call_event_action(
            event_id,
            "reject",
            payload=request_payload,
        )
        await self._record_action(
            AdminActionType.EVENT_REJECT,
            "event",
            str(event_id),
            "Rejected event",
            result,
            actor_user_id=actor_user_id,
            before={"request": request_payload},
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def resolve_event(
        self,
        event_id: UUID,
        dto: EventModerationCommandDTO,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        payload = {}
        if dto.resolved_by_user_id is not None:
            payload["resolved_by_user_id"] = str(dto.resolved_by_user_id)
        if dto.notes is not None:
            payload["notes"] = dto.notes
        if dto.resolution is not None:
            payload["resolution"] = dto.resolution
        result = await self.gateway_client.call_event_action(
            event_id,
            "resolve",
            payload=payload,
        )
        await self._record_action(
            AdminActionType.EVENT_RESOLVE,
            "event",
            str(event_id),
            "Resolved event",
            result,
            actor_user_id=actor_user_id,
            before={"request": payload},
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def cancel_event(
        self,
        event_id: UUID,
        notes: str | None = None,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        request_payload = {"notes": notes} if notes else {}
        result = await self.gateway_client.call_event_action(
            event_id,
            "cancel",
            payload=request_payload,
        )
        await self._record_action(
            AdminActionType.EVENT_CANCEL,
            "event",
            str(event_id),
            "Cancelled event",
            result,
            actor_user_id=actor_user_id,
            before={"request": request_payload},
            after=result,
            correlation_id=correlation_id,
        )
        return result

    async def get_users(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> UserListDTO:
        result = await self.gateway_client.list_users(limit=limit, offset=offset)
        items = [self.mapper.user_to_dto(item) for item in result.get("items", [])]
        return UserListDTO(
            items=items,
            total=int(result.get("total", len(items))),
            limit=limit,
            offset=offset,
        )

    async def get_user(self, user_id: UUID) -> UserSummaryDTO | None:
        result = await self.gateway_client.get_user(user_id)
        if not result:
            return None
        return self.mapper.user_to_dto(result)

    async def get_user_permissions(self, user_id: UUID) -> dict:
        return await self.gateway_client.get_user_permissions(user_id)

    async def list_roles(self) -> dict:
        return await self.gateway_client.list_roles()

    @transactional()
    async def create_role(
        self,
        dto: RoleCreateDTO,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        result = await self.gateway_client.create_role(dto.name, dto.permissions)
        await self._record_action(
            AdminActionType.USER_ROLE,
            "role",
            str(result.get("name", dto.name)),
            f"Created role {dto.name}",
            result,
            actor_user_id=actor_user_id,
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def set_role_permissions(
        self,
        role_name: str,
        dto: RolePermissionsUpdateDTO,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        before = await self.gateway_client.list_roles()
        result = await self.gateway_client.set_role_permissions(
            role_name,
            dto.permissions,
        )
        await self._record_action(
            AdminActionType.USER_ROLE,
            "role",
            str(result.get("name", role_name)),
            f"Updated role permissions for {role_name}",
            result,
            actor_user_id=actor_user_id,
            before=before,
            after=result,
            correlation_id=correlation_id,
        )
        return result

    async def list_permissions(self) -> dict:
        return await self.gateway_client.list_permissions()

    @transactional()
    async def create_permission(
        self,
        name: str,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        result = await self.gateway_client.create_permission(name)
        await self._record_action(
            AdminActionType.USER_ROLE,
            "permission",
            str(result.get("name", name)),
            f"Created permission {name}",
            result,
            actor_user_id=actor_user_id,
            after=result,
            correlation_id=correlation_id,
        )
        return result

    @transactional()
    async def set_user_status(
        self,
        user_id: UUID,
        dto: UserStatusUpdateDTO,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> UserSummaryDTO | None:
        before = await self.gateway_client.get_user(user_id)
        result = await self.gateway_client.set_user_status(user_id, dto.is_active)
        if not result:
            return None
        await self._record_action(
            AdminActionType.USER_STATUS,
            "user",
            str(user_id),
            "Updated user status",
            result,
            actor_user_id=actor_user_id,
            before=before,
            after=result,
            correlation_id=correlation_id,
        )
        return self.mapper.user_to_dto(result)

    @transactional()
    async def assign_role(
        self,
        user_id: UUID,
        dto: UserRoleGrantDTO,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> UserSummaryDTO | None:
        before = await self.gateway_client.get_user(user_id)
        result = await self.gateway_client.assign_role(
            user_id,
            dto.role_name,
        )
        if not result:
            return None
        await self._record_action(
            AdminActionType.USER_ROLE,
            "user",
            str(user_id),
            f"Granted role {dto.role_name}",
            result,
            actor_user_id=actor_user_id,
            before=before,
            after=result,
            correlation_id=correlation_id,
        )
        return self.mapper.user_to_dto(result)

    @transactional()
    async def revoke_role(
        self,
        user_id: UUID,
        role_name: str,
        actor_user_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> UserSummaryDTO | None:
        before = await self.gateway_client.get_user(user_id)
        result = await self.gateway_client.revoke_role(user_id, role_name)
        if not result:
            return None
        await self._record_action(
            AdminActionType.USER_ROLE,
            "user",
            str(user_id),
            f"Revoked role {role_name}",
            result,
            actor_user_id=actor_user_id,
            before=before,
            after=result,
            correlation_id=correlation_id,
        )
        return self.mapper.user_to_dto(result)

    async def get_profile_summary(self, user_id: UUID) -> ProfileSummaryDTO:
        profile = await self.gateway_client.get_profile(user_id)
        rating = await self.gateway_client.get_rating_profile(user_id)
        permissions = await self.gateway_client.get_user_permissions(user_id)
        return self.mapper.profile_summary_to_dto(
            {
                "profile": profile,
                "rating": rating,
                "permissions": permissions.get("permissions", []),
            }
        )

    async def get_audit_actions(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> AdminActionListDTO:
        actions = await self.action_repository.get_actions(
            limit=limit,
            offset=offset,
            action_type=action_type,
            actor_user_id=actor_user_id,
        )
        total = await self.action_repository.count_actions(
            action_type=action_type,
            actor_user_id=actor_user_id,
        )
        return AdminActionListDTO(
            items=[self.mapper.action_to_dto(item) for item in actions],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_saved_filters(
        self,
        limit: int = 100,
        offset: int = 0,
        actor_user_id: UUID | None = None,
    ) -> SavedFilterListDTO:
        filters = await self.filter_repository.get_filters(
            actor_user_id=actor_user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.filter_repository.count_filters(
            actor_user_id=actor_user_id,
        )
        return SavedFilterListDTO(
            items=[self.mapper.filter_to_dto(item) for item in filters],
            total=total,
            limit=limit,
            offset=offset,
        )

    @transactional()
    async def save_filter(
        self,
        dto: SavedFilterCreateDTO,
        correlation_id: str | None = None,
    ) -> SavedFilterDTO:
        saved_filter = SavedFilter(
            id=uuid4(),
            actor_user_id=dto.actor_user_id,
            name=dto.name,
            scope=dto.scope,
            criteria=dto.criteria,
        )
        saved = await self.filter_repository.save(saved_filter)
        await self._record_action(
            AdminActionType.FILTER_CREATE,
            "filter",
            str(saved.id),
            f"Saved filter {saved.name}",
            {
                "scope": saved.scope,
                "criteria": saved.criteria,
            },
            actor_user_id=dto.actor_user_id,
            after={
                "scope": saved.scope,
                "criteria": saved.criteria,
            },
            correlation_id=correlation_id,
        )
        return self.mapper.filter_to_dto(saved)

    async def _record_action(
        self,
        action_type: AdminActionType,
        entity_type: str,
        entity_id: str,
        summary: str,
        payload: dict | None = None,
        *,
        actor_user_id: UUID | None = None,
        before: dict | None = None,
        after: dict | None = None,
        correlation_id: str | None = None,
    ) -> None:
        await self.action_repository.save(
            AdminAction(
                id=uuid4(),
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                summary=summary,
                actor_user_id=actor_user_id,
                payload=payload,
                before=before,
                after=after,
                correlation_id=correlation_id,
            )
        )
