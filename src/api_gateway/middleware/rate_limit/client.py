from typing import Protocol


class RedisRateLimitClient(Protocol):
    async def incr(self, key: str) -> int:
        ...

    async def expire(self, key: str, seconds: int) -> object:
        ...
