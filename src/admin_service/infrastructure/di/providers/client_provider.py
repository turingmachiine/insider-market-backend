from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide

from src.admin_service.application.ports import AdminGatewayClient
from src.admin_service.core.config import AdminSettings
from src.admin_service.infrastructure.clients import HttpAdminGatewayClient


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    async def provide_http_client(
        settings: AdminSettings,
    ) -> AsyncIterable[httpx.AsyncClient]:
        client = httpx.AsyncClient(timeout=settings.ADMIN_CLIENT_TIMEOUT_SECONDS)
        yield client
        await client.aclose()

    @provide
    @staticmethod
    def provide_admin_gateway_client(
        settings: AdminSettings,
        http_client: httpx.AsyncClient,
    ) -> AdminGatewayClient:
        return HttpAdminGatewayClient(settings=settings, http_client=http_client)
