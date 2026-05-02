from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.backend.api_gateway.services.identity import JwtIdentityExtractor


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        limit_per_minute: int,
        by_jwt: bool,
        jwt_secret: str = "change-me",
        jwt_algorithm: str = "HS256",
    ) -> None:
        super().__init__(app)
        self._limit_per_minute = limit_per_minute
        self._by_jwt = by_jwt
        self._identity_extractor = JwtIdentityExtractor(jwt_secret, jwt_algorithm)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        redis_client = getattr(request.app.state, "redis", None)
        if redis_client is None:
            return await call_next(request)

        identifier = self._identifier(request)
        endpoint = request.url.path
        key = f"ratelimit:{identifier}:{endpoint}"
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, 60)
        if current > self._limit_per_minute:
            return JSONResponse(
                {"detail": "Too Many Requests"},
                status_code=429,
                headers={"Retry-After": "60"},
            )
        return await call_next(request)

    def _identifier(self, request: Request) -> str:
        if self._by_jwt:
            user_id = self._identity_extractor.extract_user_id(
                request.headers.get("authorization")
            )
            if user_id:
                return f"user:{user_id}"
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
