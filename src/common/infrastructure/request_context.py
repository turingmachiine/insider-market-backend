from uuid import UUID

from fastapi import Request

from src.common.application.request_context import (
    RequestContext,
    RequestContextProvider,
)


class FastAPIRequestContextProvider(RequestContextProvider):
    def __init__(self, request: Request) -> None:
        self.request = request

    def get_context(self) -> RequestContext:
        user_id = getattr(self.request.state, "user_id", None)
        return RequestContext(
            correlation_id=getattr(self.request.state, "request_id", None),
            user_id=user_id if isinstance(user_id, UUID) else None,
            service_name=getattr(self.request.state, "service_name", None),
        )


__all__ = ["FastAPIRequestContextProvider"]
