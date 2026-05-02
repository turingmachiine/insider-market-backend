from dishka import Provider, Scope, provide

from src.backend.auth_service.application.repository import AuthRepository
from src.backend.auth_service.application.service import AuthService
from src.backend.auth_service.core.config import AuthSettings
from src.backend.auth_service.infrastructure.cache.permissions_cache import (
    PermissionsCache,
)


class ServiceProvider(Provider):
    """Провайдер application services auth service."""

    scope = Scope.REQUEST

    @provide
    def provide_auth_service(
        self,
        repository: AuthRepository,
        permissions_cache: PermissionsCache,
        settings: AuthSettings,
    ) -> AuthService:
        return AuthService(repository, permissions_cache, settings)
