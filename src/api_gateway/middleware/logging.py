import time
from datetime import UTC, datetime

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from src.api_gateway.services.identity import JwtIdentityExtractor
from src.api_gateway.services.statistics import RedisGatewayStatistics


class AccessLogRecord:
    def __init__(
        self,
        timestamp: str,
        method: str,
        path: str,
        status: int,
        duration_ms: float,
        client_ip: str | None,
        user_id: str | None,
    ) -> None:
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.duration_ms = duration_ms
        self.client_ip = client_ip
        self.user_id = user_id

    def to_log_fields(self) -> dict[str, object]:
        return {
            "access_timestamp": self.timestamp,
            "method": self.method,
            "path": self.path,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "client_ip": self.client_ip,
            "user_id": self.user_id,
        }


class AccessLogRecordFactory:
    def __init__(self, identity_extractor: JwtIdentityExtractor) -> None:
        self._identity_extractor = identity_extractor

    def create(
        self,
        request: Request,
        status_code: int,
        duration_ms: float,
    ) -> AccessLogRecord:
        return AccessLogRecord(
            timestamp=datetime.now(UTC).isoformat(),
            method=request.method,
            path=request.url.path,
            status=status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
            user_id=self._identity_extractor.extract_user_id(
                request.headers.get("authorization")
            ),
        )


class JsonAccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        stats_ttl_seconds: int = 300,
        jwt_secret: str = "change-me",
        jwt_algorithm: str = "HS256",
    ) -> None:
        super().__init__(app)
        identity_extractor = JwtIdentityExtractor(jwt_secret, jwt_algorithm)
        self._logger = structlog.get_logger("api_gateway")
        self._record_factory = AccessLogRecordFactory(identity_extractor)
        self._statistics = RedisGatewayStatistics(stats_ttl_seconds)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        started_at = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            status_code = response.status_code if response is not None else 500
            record = self._record_factory.create(request, status_code, duration_ms)
            if record.user_id is not None:
                structlog.contextvars.bind_contextvars(user_id=record.user_id)

            redis_client = getattr(request.app.state, "redis", None)
            await self._statistics.increment(
                redis_client, request.url.path, status_code
            )
