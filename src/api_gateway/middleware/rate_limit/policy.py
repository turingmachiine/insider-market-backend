from typing import cast

from starlette.datastructures import Headers
from starlette.types import Scope

from src.api_gateway.constants import RATE_LIMIT_WINDOW_SECONDS
from src.api_gateway.services.identity import JwtIdentityExtractor

from .client import RedisRateLimitClient
from .policy_model import RateLimitPolicy


def get_redis_rate_limit_client(scope: Scope) -> RedisRateLimitClient | None:
    scope_app = scope.get("app")
    client = getattr(getattr(scope_app, "state", None), "redis", None)
    return cast(RedisRateLimitClient | None, client)


def rate_limit_identifier(
    *,
    headers: Headers,
    client_host: str | None,
    by_jwt: bool,
    identity_extractor: JwtIdentityExtractor,
) -> str:
    if by_jwt:
        user_id = identity_extractor.extract_user_id(headers.get("authorization"))
        if user_id:
            return f"user:{user_id}"
    return f"ip:{client_host or 'unknown'}"


def rate_limit_key(policy: RateLimitPolicy, identifier: str, path: str) -> str:
    if policy.name == "default":
        return f"ratelimit:{identifier}:{path}"
    return f"ratelimit:{policy.name}:{identifier}:{path}"


async def increment_rate_limit(
    redis_client: RedisRateLimitClient,
    key: str,
    limit_per_minute: int,
) -> bool:
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, RATE_LIMIT_WINDOW_SECONDS)
    return current > limit_per_minute
