from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide

from src.etl_service.core.config import ETLSettings


class HttpClientProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def provide_http_client(
        self,
        settings: ETLSettings,
    ) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=str(settings.RUMOR_SERVICE_URL).rstrip("/"),
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        ) as http_client:
            yield http_client
