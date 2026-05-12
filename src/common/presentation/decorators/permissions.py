from collections.abc import Callable
from typing import Annotated, Any, cast

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission, normalize_permission

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]

BEARER_TOKEN_MISSING_DETAIL = "Missing bearer token"
AUTH_CONTEXT_MISSING_DETAIL = "Missing authenticated request context"
PERMISSION_DENIED_DETAIL = "Permission denied"


def require_permission(
    permission: Permission | str,
) -> Callable[..., UserContext]:
    required_permission = normalize_permission(permission)

    def dependency(
        request: Request,
        credentials: BearerCredentials,
    ) -> UserContext:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=BEARER_TOKEN_MISSING_DETAIL,
            )

        user_context = getattr(request.state, "user_context", None)
        if user_context is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_CONTEXT_MISSING_DETAIL,
            )

        if not isinstance(user_context, UserContext):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_CONTEXT_MISSING_DETAIL,
            )

        if not user_context.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=PERMISSION_DENIED_DETAIL,
            )

        request.state.user_id = user_context.user_id
        request.state.permissions = user_context.permissions
        structlog.contextvars.bind_contextvars(user_id=str(user_context.user_id))
        return user_context

    dependency_any = cast(Any, dependency)
    dependency_any.__auth_required__ = True
    dependency_any.__required_permission__ = required_permission
    return dependency
