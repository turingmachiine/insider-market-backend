from abc import ABC, abstractmethod
from uuid import UUID

from src.auth_service.domain.entities import RefreshToken


class IRefreshTokenRepository(ABC):
    """Interface for persisted refresh token sessions."""

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    async def revoke_all_for_roles(self, role_names: list[str]) -> None:
        pass
