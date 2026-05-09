from abc import ABC, abstractmethod
from uuid import UUID


class AdminGatewayClient(ABC):
    @abstractmethod
    async def get_health(self, service: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_event_moderation_queue(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def call_event_action(
        self,
        event_id: UUID,
        action: str,
        payload: dict | None = None,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def list_users(self, limit: int = 100, offset: int = 0) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: UUID) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_user_permissions(self, user_id: UUID) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def set_user_status(self, user_id: UUID, is_active: bool) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def assign_role(
        self,
        user_id: UUID,
        role_name: str,
        permissions: list[str],
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_profile(self, user_id: UUID) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_rating_profile(self, user_id: UUID) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def get_rating_leaderboard(self, limit: int = 10) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def list_profiles(self, limit: int = 100, offset: int = 0) -> dict:
        raise NotImplementedError
