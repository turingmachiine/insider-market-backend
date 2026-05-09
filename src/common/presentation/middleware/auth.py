from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from re import Pattern
from typing import Protocol

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from src.common.application.security import TokenError, decode_access_token

AUTHORIZATION_HEADER = "Authorization"
BEARER_SCHEME = "bearer"
API_PREFIX = "/api/"
BEARER_TOKEN_MISSING_DETAIL = "Missing bearer token"
BEARER_TOKEN_INVALID_DETAIL = "Invalid bearer token"
IGNORING_INVALID_BEARER_TOKEN_MESSAGE = "Ignoring invalid bearer token on public path"


class HasJwtConfig(Protocol):
    JWT_SECRET: str
    JWT_ALGORITHM: str


@dataclass(frozen=True)
class ProtectedRoute:
    path_regex: Pattern[str]
    methods: frozenset[str]

    def matches(self, path: str, method: str) -> bool:
        return method in self.methods and bool(self.path_regex.match(path))


def collect_protected_routes(app: FastAPI) -> list[ProtectedRoute]:
    protected_routes: list[ProtectedRoute] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        if bool(getattr(route.endpoint, "__auth_required__", False)):
            protected_routes.append(
                ProtectedRoute(
                    path_regex=route.path_regex,
                    methods=frozenset(route.methods or set()),
                )
            )
            continue

        dependant = getattr(route, "dependant", None)
        dependencies = getattr(dependant, "dependencies", []) if dependant else []
        if any(
            bool(getattr(dependency.call, "__auth_required__", False))
            for dependency in dependencies
        ):
            protected_routes.append(
                ProtectedRoute(
                    path_regex=route.path_regex,
                    methods=frozenset(route.methods or set()),
                )
            )
    return protected_routes


def _is_public_path(path: str, is_protected: bool) -> bool:
    return not path.startswith(API_PREFIX) or not is_protected


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


def build_jwt_auth_middleware(
    settings: HasJwtConfig,
    protected_routes: list[ProtectedRoute] | None = None,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    routes = protected_routes if protected_routes is not None else []

    async def jwt_auth_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        token = _extract_bearer_token(request.headers.get(AUTHORIZATION_HEADER, ""))
        is_protected = any(
            route.matches(request.url.path, request.method) for route in routes
        )

        if _is_public_path(request.url.path, is_protected):
            if token is not None:
                try:
                    payload = decode_access_token(token, settings)
                except TokenError:
                    structlog.get_logger(__name__).warning(
                        IGNORING_INVALID_BEARER_TOKEN_MESSAGE,
                        path=request.url.path,
                    )
                else:
                    _bind_auth_context(request, payload)
            return await call_next(request)

        if token is None:
            return _unauthorized(BEARER_TOKEN_MISSING_DETAIL)

        try:
            payload = decode_access_token(token, settings)
        except TokenError:
            return _unauthorized(BEARER_TOKEN_INVALID_DETAIL)

        _bind_auth_context(request, payload)
        return await call_next(request)

    return jwt_auth_middleware
