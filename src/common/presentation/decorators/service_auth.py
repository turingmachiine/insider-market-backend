from collections.abc import Callable
from typing import Any, cast

import structlog
from fastapi import HTTPException, Request, status

from src.common.application.service_context import ServiceContext

SERVICE_AUTH_CONTEXT_MISSING_DETAIL = "Missing authenticated service context"
SERVICE_SCOPE_DENIED_DETAIL = "Service scope denied"


def require_service_auth(*required_scopes: str) -> Callable[..., ServiceContext]:
    scopes = frozenset(required_scopes)

    def dependency(request: Request) -> ServiceContext:
        service_context = getattr(request.state, "service_context", None)
        if service_context is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=SERVICE_AUTH_CONTEXT_MISSING_DETAIL,
            )

        if not isinstance(service_context, ServiceContext):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=SERVICE_AUTH_CONTEXT_MISSING_DETAIL,
            )

        missing_scopes = [
            scope for scope in scopes if not service_context.has_scope(scope)
        ]
        if missing_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=SERVICE_SCOPE_DENIED_DETAIL,
            )

        request.state.service_name = service_context.service_name
        structlog.contextvars.bind_contextvars(
            service_name=service_context.service_name,
        )
        return service_context

    dependency_any = cast(Any, dependency)
    dependency_any.__service_auth_required__ = True
    dependency_any.__required_service_scopes__ = scopes
    return dependency
