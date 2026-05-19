from collections.abc import AsyncIterable
from uuid import UUID

import httpx
from dishka import Provider, Scope, provide

from src.auth_service.application.ports import UserProvisioningPort
from src.auth_service.core.config import AuthSettings
from src.auth_service.infrastructure.clients import UserProvisioningClient


class NoopUserProvisioningClient(UserProvisioningPort):
    async def provision_user(
        self,
        user_id: UUID,
        email: str,
        correlation_id: str | None = None,
    ) -> None:
        return None


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_http_client(
        self,
        settings: AuthSettings,
    ) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            timeout=settings.PROVISIONING_REQUEST_TIMEOUT_SECONDS,
        ) as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def provide_user_provisioning_port(
        self,
        http_client: httpx.AsyncClient,
        settings: AuthSettings,
    ) -> UserProvisioningPort:
        if not settings.USER_PROVISIONING_ENABLED:
            return NoopUserProvisioningClient()
        return UserProvisioningClient(http_client, settings)
