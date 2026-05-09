from abc import ABC, abstractmethod
from uuid import UUID

from src.admin_service.domain.entities import AdminAction, AdminActionType


class IAdminActionRepository(ABC):
    @abstractmethod
    async def get_actions(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> list[AdminAction]:
        raise NotImplementedError

    @abstractmethod
    async def count_actions(
        self,
        action_type: AdminActionType | None = None,
        actor_user_id: UUID | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def save(self, action: AdminAction) -> AdminAction:
        raise NotImplementedError
