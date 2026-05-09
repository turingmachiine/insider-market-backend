from collections.abc import AsyncIterable

import redis.asyncio as redis
from dishka import Provider, Scope, provide

from src.auth_service.core.config import AuthSettings
from src.auth_service.infrastructure.cache.permissions_cache import PermissionsCache


class CacheProvider(Provider):
    """Провайдер зависимостей cache слоя."""

    scope = Scope.APP

    @provide
    async def provide_permissions_cache(
        self,
        settings: AuthSettings,
    ) -> AsyncIterable[PermissionsCache]:
        """Создание cache adapter для permissions."""
        redis_client = (
            redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        )
        try:
            yield PermissionsCache(
                redis_client,
                ttl_seconds=settings.PERMISSIONS_CACHE_TTL,
            )
        finally:
            if redis_client is not None:
                await redis_client.aclose()
