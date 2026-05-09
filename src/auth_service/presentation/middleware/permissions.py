from collections.abc import Callable
from typing import Annotated, Any, cast

import structlog
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]

BEARER_TOKEN_MISSING_DETAIL = "Missing bearer token"
AUTH_CONTEXT_MISSING_DETAIL = "Missing authenticated request context"
PERMISSION_DENIED_DETAIL = "Permission denied"


def require_permission(
    permission: str,
) -> Callable[..., dict[str, Any]]:
    @inject
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

        permissions = set(payload.get("permissions", []))
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=PERMISSION_DENIED_DETAIL,
            )
        request.state.user_id = payload["sub"]
        request.state.permissions = permissions
        structlog.contextvars.bind_contextvars(user_id=str(payload["sub"]))
        return cast(dict[str, Any], payload)

    return dependency
