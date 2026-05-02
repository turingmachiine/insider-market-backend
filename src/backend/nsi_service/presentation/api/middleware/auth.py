from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from src.backend.nsi_service.core.config import settings

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
