from uuid import uuid4

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp, request_id_header: str = "X-Request-ID") -> None:
        self.app = app
        self._request_id_header = request_id_header

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_headers = MutableHeaders(scope=scope)
        request_id = request_headers.get(self._request_id_header) or str(uuid4())
        user_id = request_headers.get("X-User-ID")
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_id=user_id,
        )
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers[self._request_id_header] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except BaseException:
            structlog.get_logger(__name__).exception(
                "Unhandled request exception",
                method=scope.get("method"),
                path=scope.get("path"),
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
