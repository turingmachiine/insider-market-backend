from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.admin_service.application.dto import SavedFilterCreateDTO, UserStatusUpdateDTO
from src.admin_service.application.mappers import AdminMapper
from src.admin_service.application.ports import AdminGatewayClient
from src.admin_service.application.usecases import AdminUseCases
from src.admin_service.domain.entities import AdminAction, AdminActionType, SavedFilter
from src.admin_service.domain.interfaces.repositories import (
    IAdminActionRepository,
    ISavedFilterRepository,
)
from src.common.domain.interfaces import TransactionManager


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self._in_transaction = False
        self._in_nested = False

    async def begin(self) -> None:
        self._in_transaction = True

    async def begin_nested(self) -> None:
        self._in_nested = True

    async def commit(self) -> None:  # NOSONAR(S4144)
        self._in_transaction = False
        self._in_nested = False

    async def rollback(self) -> None:  # NOSONAR(S4144)
        self._in_transaction = False
        self._in_nested = False

    async def flush(self) -> None:  # NOSONAR(S4144)
        pass

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    @property
    def in_nested(self) -> bool:
        return self._in_nested


class FakeAdminGatewayClient(AdminGatewayClient):
    async def list_roles(self) -> dict:
        return {}

    async def create_role(self, name: str, permissions: list[str]) -> dict:
        return {}

    async def set_role_permissions(
        self, role_name: str, permissions: list[str]
    ) -> dict:
        return {}

    async def list_permissions(self) -> dict:
        return {}

    async def create_permission(self, name: str) -> dict:
        return {}

    async def revoke_role(self, user_id: UUID, role_name: str) -> dict:
        return {}

    async def get_health(self, service: str) -> dict:
        return {"status": "healthy", "version": "1.0.0", "service": service}

    async def get_event_moderation_queue(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        return {
            "items": [{"id": "event-1"}],
            "total": 3,
            "limit": limit,
            "offset": offset,
        }

    async def call_event_action(
        self,
        event_id: UUID,
        action: str,
        payload: dict | None = None,
    ) -> dict:
        return {"event_id": str(event_id), "action": action, "payload": payload or {}}

    async def list_users(self, limit: int = 100, offset: int = 0) -> dict:
        return {
            "items": [
                {
                    "id": str(uuid4()),
                    "email": "admin@example.com",
                    "is_active": True,
                    "roles": ["admin"],
                    "permissions": ["admin:read", "admin:write"],
                    "created_at": datetime.now(UTC).isoformat(),
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset,
        }

    async def get_user(self, user_id: UUID) -> dict:
        return {
            "id": str(user_id),
            "email": "admin@example.com",
            "is_active": True,
            "roles": ["admin"],
            "permissions": ["admin:read", "admin:write"],
            "created_at": datetime.now(UTC).isoformat(),
        }

    async def get_user_permissions(self, user_id: UUID) -> dict:
        return {"user_id": str(user_id), "permissions": ["admin:read"]}

    async def set_user_status(self, user_id: UUID, is_active: bool) -> dict:
        return {
            "id": str(user_id),
            "email": "admin@example.com",
            "is_active": is_active,
            "roles": ["admin"],
            "permissions": ["admin:read", "admin:write"],
            "created_at": datetime.now(UTC).isoformat(),
        }

    async def assign_role(
        self,
        user_id: UUID,
        role_name: str,
    ) -> dict:
        return {
            "id": str(user_id),
            "email": "admin@example.com",
            "is_active": True,
            "roles": ["admin", role_name],
            "permissions": sorted({"admin:read", "admin:write"}),
            "created_at": datetime.now(UTC).isoformat(),
        }

    async def get_profile(self, user_id: UUID) -> dict:
        return {"id": str(user_id), "display_name": "Scout"}

    async def get_rating_profile(self, user_id: UUID) -> dict:
        return {"user_id": str(user_id), "rating": 1200}

    async def get_rating_leaderboard(self, limit: int = 10) -> dict:
        return {"items": [{"user_id": str(uuid4())}], "total": 7, "limit": limit}

    async def list_profiles(self, limit: int = 100, offset: int = 0) -> dict:
        return {
            "items": [{"id": str(uuid4())}],
            "total": 4,
            "limit": limit,
            "offset": offset,
        }


class FakeAdminActionRepository(IAdminActionRepository):
    def __init__(self) -> None:
        self.items: list[AdminAction] = []

    async def get_actions(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AdminAction]:
        actions = self.items
        if action_type is not None:
            actions = [item for item in actions if item.action_type == action_type]
        if actor_user_id is not None:
            actions = [item for item in actions if item.actor_user_id == actor_user_id]
        return actions[offset : offset + limit]

    async def count_actions(
        self,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        return len(
            await self.get_actions(
                limit=10_000,
                offset=0,
                action_type=action_type,
                actor_user_id=actor_user_id,
            )
        )

    async def save(self, action: AdminAction) -> AdminAction:
        self.items.append(action)
        return action


class FakeSavedFilterRepository(ISavedFilterRepository):
    def __init__(self) -> None:
        self.items: list[SavedFilter] = []

    async def get_filters(
        self,
        actor_user_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SavedFilter]:
        filters = self.items
        if actor_user_id is not None:
            filters = [item for item in filters if item.actor_user_id == actor_user_id]
        return filters[offset : offset + limit]

    async def count_filters(self, actor_user_id: UUID | None = None) -> int:
        return len(
            await self.get_filters(
                actor_user_id=actor_user_id,
                limit=10_000,
                offset=0,
            )
        )

    async def save(self, saved_filter: SavedFilter) -> SavedFilter:
        self.items.append(saved_filter)
        return saved_filter


def create_use_cases() -> (
    tuple[AdminUseCases, FakeAdminActionRepository, FakeSavedFilterRepository]
):
    action_repository = FakeAdminActionRepository()
    filter_repository = FakeSavedFilterRepository()
    return (
        AdminUseCases(
            gateway_client=FakeAdminGatewayClient(),
            action_repository=action_repository,
            filter_repository=filter_repository,
            mapper=AdminMapper(),
            transaction_manager=FakeTransactionManager(),
        ),
        action_repository,
        filter_repository,
    )


@pytest.mark.asyncio
async def test_dashboard_overview_aggregates_counts() -> None:
    use_cases, _, _ = create_use_cases()

    dashboard = await use_cases.get_dashboard_overview()

    assert dashboard.event_moderation_queue_size == 3
    assert dashboard.users_total == 1
    assert dashboard.rating_leaderboard_size == 7
    assert dashboard.profiles_total == 4
    assert dashboard.services[0].status == "healthy"


@pytest.mark.asyncio
async def test_save_filter_records_action() -> None:
    use_cases, action_repository, filter_repository = create_use_cases()
    actor_user_id = uuid4()

    saved_filter = await use_cases.save_filter(
        SavedFilterCreateDTO(
            actor_user_id=actor_user_id,
            name="Moderation queue",
            scope="event",
            criteria={"status": ["pending"]},
        ),
        correlation_id="filter-request",
    )

    assert saved_filter.name == "Moderation queue"
    assert len(filter_repository.items) == 1
    assert len(action_repository.items) == 1
    assert action_repository.items[0].action_type == AdminActionType.FILTER_CREATE
    assert action_repository.items[0].after == {
        "scope": "event",
        "criteria": {"status": ["pending"]},
    }
    assert action_repository.items[0].correlation_id == "filter-request"


@pytest.mark.asyncio
async def test_user_status_action_records_before_after() -> None:
    use_cases, action_repository, _ = create_use_cases()
    actor_user_id = uuid4()
    user_id = uuid4()

    result = await use_cases.set_user_status(
        user_id,
        dto=UserStatusUpdateDTO(is_active=False),
        actor_user_id=actor_user_id,
        correlation_id="status-request",
    )

    assert result is not None
    assert action_repository.items[0].action_type == AdminActionType.USER_STATUS
    assert action_repository.items[0].before is not None
    assert action_repository.items[0].before["is_active"] is True
    assert action_repository.items[0].after is not None
    assert action_repository.items[0].after["is_active"] is False
    assert action_repository.items[0].correlation_id == "status-request"
