from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.domain.entities import PasswordResetToken
from src.auth_service.domain.interfaces.repositories import (
    IPasswordResetTokenRepository,
)
from src.auth_service.infrastructure.db.tables import password_reset_tokens_table


class PasswordResetTokenRepository(IPasswordResetTokenRepository):
    """Database repository for password reset tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = PasswordResetToken

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        query = select(self.model).where(
            password_reset_tokens_table.c.token_hash == token_hash
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def save(
        self, password_reset_token: PasswordResetToken
    ) -> PasswordResetToken:
        self.session.add(password_reset_token)
        await self.session.flush()
        return password_reset_token

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        await self.session.execute(
            update(password_reset_tokens_table)
            .where(password_reset_tokens_table.c.user_id == user_id)
            .where(password_reset_tokens_table.c.used_at.is_(None))
            .values(used_at=datetime.now(UTC))
        )
