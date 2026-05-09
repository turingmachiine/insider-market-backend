import logging
import time

import redis.asyncio as redis


class RedisGatewayStatistics:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self._ttl_seconds = ttl_seconds
        self._logger = logging.getLogger("api_gateway.stats")

    async def increment(
        self, redis_client: redis.Redis | None, endpoint: str, status_code: int
    ) -> None:
        if redis_client is None:
            return
        try:
            window = int(time.time() // self._ttl_seconds)
            key = f"stats:{window}:{endpoint}:{status_code}"
            await redis_client.incr(key)
            await redis_client.expire(key, self._ttl_seconds)
        except Exception:
            self._logger.exception("Failed to update gateway statistics")
