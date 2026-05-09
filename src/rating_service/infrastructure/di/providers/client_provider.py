from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide

from src.rating_service.application.ports import ProfileBalancePort
from src.rating_service.core.config import RatingSettings
from src.rating_service.infrastructure.clients import ProfileBalanceClient


class ClientProvider(Provider):
    scope = Scope.APP

    @provide
    @staticmethod
    async def provide_http_client(
        settings: RatingSettings,
    ) -> AsyncIterable[httpx.AsyncClient]:
        timeout = httpx.Timeout(settings.REWARD_REQUEST_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            yield client

    @provide(scope=Scope.REQUEST)
    @staticmethod
    def provide_profile_balance_port(
        settings: RatingSettings,
        http_client: httpx.AsyncClient,
    ) -> ProfileBalancePort:
        return ProfileBalanceClient(str(settings.PROFILE_SERVICE_URL), http_client)
