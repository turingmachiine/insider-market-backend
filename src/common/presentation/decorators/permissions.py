from collections.abc import Callable
from typing import Annotated, Any, cast

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
) -> Callable[..., dict[str, Any]]:
    required_permission = normalize_permission(permission)

    def dependency(
        request: Request,
        credentials: BearerCredentials,
    ) -> dict[str, Any]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=BEARER_TOKEN_MISSING_DETAIL,
            )

        payload = getattr(request.state, "auth_payload", None)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_CONTEXT_MISSING_DETAIL,
            )

        permissions = set(getattr(request.state, "permissions", set()))
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=PERMISSION_DENIED_DETAIL,
            )

        request.state.user_id = payload["sub"]
        request.state.permissions = permissions
        structlog.contextvars.bind_contextvars(user_id=str(payload["sub"]))
        return cast(dict[str, Any], payload)

    dependency_any = cast(Any, dependency)
    dependency_any.__auth_required__ = True
    dependency_any.__required_permission__ = required_permission
    return dependency
