from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from src.api_gateway.services.identity import JwtIdentityExtractor

from .policy import (
    get_redis_rate_limit_client,
    increment_rate_limit,
    rate_limit_identifier,
    rate_limit_key,
)
from .policy_model import RateLimitPolicy


class WebSocketRateLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        limit_per_minute: int,
        by_jwt: bool,
        jwt_secret: str = "change-me",
        jwt_algorithm: str = "HS256",
    ) -> None:
        self.app = app
        self._policy = RateLimitPolicy("websocket", limit_per_minute)
        self._by_jwt = by_jwt
        self._identity_extractor = JwtIdentityExtractor(jwt_secret, jwt_algorithm)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "websocket":
            await self.app(scope, receive, send)
            return

        redis_client = get_redis_rate_limit_client(scope)
        if redis_client is None:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        path = str(scope.get("path", ""))
        client = scope.get("client")
        client_host = client[0] if client else None
        identifier = rate_limit_identifier(
            headers=headers,
            client_host=client_host,
            by_jwt=self._by_jwt,
            identity_extractor=self._identity_extractor,
        )
        exceeded = await increment_rate_limit(
            redis_client,
            rate_limit_key(self._policy, identifier, path),
            self._policy.limit_per_minute,
        )
        if exceeded:
            await send(
                {
                    "type": "websocket.close",
                    "code": 4408,
                    "reason": "Too Many Requests",
                }
            )
            return

        await self.app(scope, receive, send)
