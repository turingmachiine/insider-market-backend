from dishka import Provider, Scope, provide

from src.auth_service.application.service import AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.interfaces.repositories import (
    IAuditLogRepository,
    IPasswordResetTokenRepository,
    IPermissionRepository,
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
        permission_repository: IPermissionRepository,
        refresh_token_repository: IRefreshTokenRepository,
        password_reset_token_repository: IPasswordResetTokenRepository,
        audit_log_repository: IAuditLogRepository,
        settings: AuthSettings,
    ) -> AuthService:
        return AuthService(
            user_repository,
            role_repository,
            permission_repository,
            refresh_token_repository,
            password_reset_token_repository,
            audit_log_repository,
            settings,
        )
