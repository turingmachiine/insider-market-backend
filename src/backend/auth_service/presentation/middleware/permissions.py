from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.backend.auth_service.application.security import (
    TokenError,
    decode_access_token,
)
from src.backend.auth_service.core.config import AuthSettings, settings

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


def require_permission(
    permission: str,
    auth_settings: AuthSettings = settings,
) -> Callable[[Request, BearerCredentials], Awaitable[dict[str, Any]]]:
    async def dependency(
        request: Request,
        credentials: BearerCredentials,
    ) -> dict[str, Any]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
            )
        try:
            payload = decode_access_token(credentials.credentials, auth_settings)
        except TokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
            )

        permissions = set(payload.get("permissions", []))
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        request.state.user_id = payload["sub"]
        request.state.permissions = permissions
        return payload

    return dependency
