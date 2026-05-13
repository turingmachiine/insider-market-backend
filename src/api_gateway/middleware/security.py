from urllib.parse import unquote

import anyio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message


class GatewaySecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        max_body_size_bytes: int,
        security_headers: dict[str, str],
    ) -> None:
        super().__init__(app)
        self._max_body_size_bytes = max_body_size_bytes
        self._security_headers = security_headers

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = unquote(request.url.path)
        if "/../" in path or path.endswith("/..") or path.startswith("../"):
            return self._with_security_headers(
                JSONResponse({"detail": "Path traversal is not allowed"}, 400)
            )

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                parsed_content_length = int(content_length)
            except ValueError:
                return self._with_security_headers(
                    JSONResponse({"detail": "Invalid Content-Length"}, 400)
                )
            if parsed_content_length > self._max_body_size_bytes:
                return self._with_security_headers(
                    JSONResponse({"detail": "Request body is too large"}, 413)
                )

        body = await request.body()
        if len(body) > self._max_body_size_bytes:
            return self._with_security_headers(
                JSONResponse({"detail": "Request body is too large"}, 413)
            )

        async def receive() -> Message:
            await anyio.lowlevel.checkpoint()
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive
        response = await call_next(request)
        return self._with_security_headers(response)

    def _with_security_headers(self, response: Response) -> Response:
        for name, value in self._security_headers.items():
            response.headers.setdefault(name, value)
        return response
