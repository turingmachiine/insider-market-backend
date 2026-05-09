from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from src.common.application.security import TokenError, decode_access_token
from src.nsi_service.core.config import settings

AUTHORIZATION_HEADER = "Authorization"
BEARER_SCHEME = "bearer"
API_PREFIX = "/api/"
BEARER_TOKEN_MISSING_DETAIL = "Missing bearer token"
BEARER_TOKEN_INVALID_DETAIL = "Invalid bearer token"
PUBLIC_PATHS = ("/health", "/openapi.json", "/api/docs", "/api/redoc")


def _extract_bearer_token(authorization: str) -> str | None:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != BEARER_SCHEME or not token:
        return None
    return token


def _extract_permissions(payload: dict[str, object]) -> set[str]:
    permissions = payload.get("permissions", [])
    if not isinstance(permissions, list):
        return set()
    if not all(isinstance(permission, str) for permission in permissions):
        return set()
    return set(permissions)


def _bind_auth_context(request: Request, payload: dict[str, object]) -> None:
    request.state.auth_payload = payload
    request.state.user_id = payload.get("sub")
    request.state.permissions = _extract_permissions(payload)
    if request.state.user_id is not None:
        structlog.contextvars.bind_contextvars(user_id=str(request.state.user_id))


def _unauthorized(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
    )


async def jwt_auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    if not request.url.path.startswith(API_PREFIX):
        return await call_next(request)

    token = _extract_bearer_token(request.headers.get(AUTHORIZATION_HEADER, ""))
    if token is None:
        return _unauthorized(BEARER_TOKEN_MISSING_DETAIL)

    try:
        payload = decode_access_token(token, settings)
    except TokenError:
        return _unauthorized(BEARER_TOKEN_INVALID_DETAIL)

    _bind_auth_context(request, payload)
    return await call_next(request)
