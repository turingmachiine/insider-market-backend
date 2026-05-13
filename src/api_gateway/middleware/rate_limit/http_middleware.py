from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.api_gateway.constants import (
    AUTH_SENSITIVE_ENDPOINTS,
    RATE_LIMIT_WINDOW_SECONDS,
)
from src.api_gateway.services.identity import JwtIdentityExtractor

from .policy import (
    get_redis_rate_limit_client,
    increment_rate_limit,
    rate_limit_identifier,
    rate_limit_key,
)
from .policy_model import RateLimitPolicy


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        limit_per_minute: int,
        public_limit_per_minute: int,
        sensitive_limit_per_minute: int,
        by_jwt: bool,
        jwt_secret: str = "change-me",
        jwt_algorithm: str = "HS256",
    ) -> None:
        super().__init__(app)
        self._limit_per_minute = limit_per_minute
        self._public_limit_per_minute = public_limit_per_minute
        self._sensitive_limit_per_minute = sensitive_limit_per_minute
        self._by_jwt = by_jwt
        self._identity_extractor = JwtIdentityExtractor(jwt_secret, jwt_algorithm)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        redis_client = get_redis_rate_limit_client(request.scope)
        if redis_client is None:
            return await call_next(request)

        policy = self._policy_for(request.method, request.url.path)
        identifier = rate_limit_identifier(
            headers=request.headers,
            client_host=request.client.host if request.client else None,
            by_jwt=self._by_jwt,
            identity_extractor=self._identity_extractor,
        )
        exceeded = await increment_rate_limit(
            redis_client,
            rate_limit_key(policy, identifier, request.url.path),
            policy.limit_per_minute,
        )
        if exceeded:
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=429,
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        return await call_next(request)

    def _policy_for(self, method: str, path: str) -> RateLimitPolicy:
        if self._is_sensitive_auth_route(method, path):
            return RateLimitPolicy("sensitive", self._sensitive_limit_per_minute)
        if method.upper() in {"GET", "HEAD", "OPTIONS"}:
            return RateLimitPolicy("public", self._public_limit_per_minute)
        return RateLimitPolicy("default", self._limit_per_minute)

    @staticmethod
    def _is_sensitive_auth_route(method: str, path: str) -> bool:
        if method.upper() != "POST" or not path.startswith("/auth/"):
            return False
        endpoint = path.rstrip("/").rsplit("/", 1)[-1]
        return endpoint in AUTH_SENSITIVE_ENDPOINTS
