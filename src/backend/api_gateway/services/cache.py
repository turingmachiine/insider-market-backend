import base64
import json
from collections.abc import Mapping
from typing import Any

import redis.asyncio as redis


class GatewayCache:
    def __init__(self, redis_client: redis.Redis | None, ttl_seconds: int) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def build_key(path: str, query_string: bytes) -> str:
        return f"cache:{path}:{query_string.decode()}"

    async def get(self, path: str, query_string: bytes) -> dict | None:
        if self._redis is None:
            return None

        raw = await self._redis.get(self.build_key(path, query_string))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        cached: dict[str, Any] = json.loads(raw)
        cached["body"] = base64.b64decode(cached["body"])
        return cached

    async def set(
        self,
        path: str,
        query_string: bytes,
        status_code: int,
        headers: Mapping[str, str],
        body: bytes,
    ) -> None:
        if self._redis is None or status_code >= 400:
            return

        payload = {
            "status_code": status_code,
            "headers": dict(headers),
            "body": base64.b64encode(body).decode(),
        }
        await self._redis.setex(
            self.build_key(path, query_string),
            self._ttl_seconds,
            json.dumps(payload),
        )

    async def invalidate_path(self, path: str) -> None:
        if self._redis is None:
            return

        keys: list[str] = []
        async for key in self._redis.scan_iter(match=f"cache:{path}:*"):
            keys.append(key)
        if keys:
            await self._redis.delete(*keys)

    async def invalidate_prefix(self, path_prefix: str) -> None:
        if self._redis is None:
            return

        keys: list[str] = []
        async for key in self._redis.scan_iter(match=f"cache:{path_prefix}*"):
            keys.append(key)
        if keys:
            await self._redis.delete(*keys)
