from dishka import Provider, Scope, provide

from src.auth_service.application.service import AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.interfaces.repositories import (
    IRoleRepository,
    IUserRepository,
)
from src.auth_service.infrastructure.cache.permissions_cache import PermissionsCache


class ServiceProvider(Provider):
    """Провайдер application services auth service."""

    scope = Scope.REQUEST

    @provide
    def provide_auth_service(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        permissions_cache: PermissionsCache,
        settings: AuthSettings,
    ) -> AuthService:
        return AuthService(
            user_repository,
            role_repository,
            permissions_cache,
            settings,
        )
