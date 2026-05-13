from dishka import Provider, Scope, provide
from fastapi import Request

from src.common.application.request_context import RequestContextProvider
from src.common.infrastructure.request_context import FastAPIRequestContextProvider


class FastAPIRequestContextDIProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_request_context_provider(
        request: Request,
    ) -> RequestContextProvider:
        return FastAPIRequestContextProvider(request)


__all__ = ["FastAPIRequestContextDIProvider"]
