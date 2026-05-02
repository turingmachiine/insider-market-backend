from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.auth_service.application.repository import AuthRepository


class RepositoryProvider(Provider):
    """Провайдер репозиториев auth service."""

    scope = Scope.REQUEST

    @provide
    def provide_auth_repository(self, session: AsyncSession) -> AuthRepository:
        return AuthRepository(session)
