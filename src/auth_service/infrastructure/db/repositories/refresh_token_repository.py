from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.domain.entities import RefreshToken
from src.auth_service.domain.interfaces.repositories import IRefreshTokenRepository
from src.auth_service.infrastructure.db.tables import refresh_tokens_table


class RefreshTokenRepository(IRefreshTokenRepository):
    """Database repository for refresh token sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = RefreshToken

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(self.model).where(
            refresh_tokens_table.c.token_hash == token_hash
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def save(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        revoked_at = datetime.now(UTC)
        query = (
            update(refresh_tokens_table)
            .where(refresh_tokens_table.c.user_id == user_id)
            .where(refresh_tokens_table.c.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self.session.execute(query)
