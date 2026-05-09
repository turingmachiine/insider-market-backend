from uuid import uuid4

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, request_id_header: str = "X-Request-ID") -> None:
        super().__init__(app)
        self._request_id_header = request_id_header

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get(self._request_id_header) or str(uuid4())
        user_id = request.headers.get("X-User-ID")
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_id=user_id,
        )
        request.state.request_id = request_id
        try:
            response = await call_next(request)
            response.headers[self._request_id_header] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()
