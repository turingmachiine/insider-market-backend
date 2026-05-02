from urllib.parse import unquote

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class GatewaySecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_body_size_bytes: int) -> None:
        super().__init__(app)
        self._max_body_size_bytes = max_body_size_bytes

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = unquote(request.url.path)
        if "/../" in path or path.endswith("/..") or path.startswith("../"):
            return JSONResponse({"detail": "Path traversal is not allowed"}, 400)

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self._max_body_size_bytes:
            return JSONResponse({"detail": "Request body is too large"}, 413)

        body = await request.body()
        if len(body) > self._max_body_size_bytes:
            return JSONResponse({"detail": "Request body is too large"}, 413)

        async def receive() -> dict:
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive
        return await call_next(request)
