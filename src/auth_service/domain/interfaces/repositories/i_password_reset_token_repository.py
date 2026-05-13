from abc import ABC, abstractmethod
from uuid import UUID

from src.auth_service.domain.entities import PasswordResetToken


class IPasswordResetTokenRepository(ABC):
    """Interface for persisted password reset tokens."""

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        pass

    @abstractmethod
    async def save(
        self, password_reset_token: PasswordResetToken
    ) -> PasswordResetToken:
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        pass
