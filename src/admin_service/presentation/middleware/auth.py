from collections.abc import Awaitable, Callable
from typing import Annotated, Any, cast

import structlog
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.admin_service.core.config import AdminSettings, settings

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]

PUBLIC_PATHS = {
    "/health",
    "/openapi.json",
    "/api/docs",
    "/api/redoc",
}


async def jwt_auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing bearer token"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid bearer token"},
        )

    request.state.user_id = payload.get("sub")
    request.state.permissions = set(payload.get("permissions", []))
    if request.state.user_id is not None:
        structlog.contextvars.bind_contextvars(user_id=str(request.state.user_id))
    return await call_next(request)


def require_permission(permission: str) -> Callable[..., dict[str, Any]]:
    @inject
    def dependency(
        request: Request,
        credentials: BearerCredentials,
        settings: FromDishka[AdminSettings],
    ) -> dict[str, Any]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
            )
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
            ) from exc

        permissions = set(payload.get("permissions", []))
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        request.state.user_id = payload.get("sub")
        request.state.permissions = permissions
        structlog.contextvars.bind_contextvars(user_id=str(payload.get("sub")))
        return cast(dict[str, Any], payload)

    return dependency
