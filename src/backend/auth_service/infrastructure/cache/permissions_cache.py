import json
from uuid import UUID

import redis.asyncio as redis


class PermissionsCache:
    def __init__(self, client: redis.Redis | None, ttl_seconds: int = 300) -> None:
        self.client = client
        self.ttl_seconds = ttl_seconds

    async def get(self, user_id: UUID) -> list[str] | None:
        if self.client is None:
            return None
        raw = await self.client.get(self._key(user_id))
        if raw is None:
            return None
        return list(json.loads(raw))

    async def set(self, user_id: UUID, permissions: list[str]) -> None:
        if self.client is None:
            return
        await self.client.setex(
            self._key(user_id),
            self.ttl_seconds,
            json.dumps(permissions),
        )

    async def invalidate(self, user_id: UUID) -> None:
        if self.client is None:
            return
        await self.client.delete(self._key(user_id))

    def _key(self, user_id: UUID) -> str:
        return f"perms:{user_id}"
