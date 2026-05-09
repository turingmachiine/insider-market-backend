from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_service.domain.interfaces.repositories import (
    IPermissionRepository,
    IRoleRepository,
    IUserRepository,
)
from src.auth_service.infrastructure.db.repositories import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)


class RepositoryProvider(Provider):
    """Провайдер репозиториев auth service."""

    scope = Scope.REQUEST

    @provide
    def provide_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)

    @provide
    def provide_permission_repository(
        self,
        session: AsyncSession,
    ) -> IPermissionRepository:
        return PermissionRepository(session)

    @provide
    def provide_role_repository(
        self,
        session: AsyncSession,
        permission_repository: IPermissionRepository,
    ) -> IRoleRepository:
        return RoleRepository(session, permission_repository)
