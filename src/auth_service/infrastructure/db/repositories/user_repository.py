from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth_service.domain.entities import Role, User
from src.auth_service.domain.interfaces.repositories import IUserRepository
from src.auth_service.infrastructure.db.tables import users_table


class UserRepository(IUserRepository):
    """Реализация репозитория пользователей."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = User

    async def get_by_email(self, email: str) -> User | None:
        query = (
            select(self.model)
            .where(users_table.c.email == email)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        query = (
            select(self.model)
            .where(users_table.c.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        query = (
            select(self.model)
            .order_by(users_table.c.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        query = select(func.count()).select_from(users_table)
        result = await self.session.execute(query)
        return int(result.scalar_one())

    async def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash, is_active=True, roles=[])
        self.session.add(user)
        await self.session.flush()
        return user

    async def save(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
