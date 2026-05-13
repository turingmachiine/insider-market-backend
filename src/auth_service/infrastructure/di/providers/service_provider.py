from dishka import Provider, Scope, provide

from src.auth_service.application.service import AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IRefreshTokenRepository,
    IRoleRepository,
    IUserRepository,
)


class ServiceProvider(Provider):
    """Провайдер application services auth service."""

    scope = Scope.REQUEST

    @provide
    def provide_auth_service(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        refresh_token_repository: IRefreshTokenRepository,
        audit_log_repository: IAuditLogRepository,
        settings: AuthSettings,
    ) -> AuthService:
        return AuthService(
            user_repository,
            role_repository,
            refresh_token_repository,
            audit_log_repository,
            settings,
        )
