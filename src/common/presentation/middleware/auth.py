from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from re import Pattern

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from src.common.application.protocols import IServiceProvider, IUserProvider
from src.common.application.security import TokenError
from src.common.application.service_context import ServiceContext
from src.common.application.user_context import UserContext
from src.common.domain.service_auth import SERVICE_AUTHORIZATION_HEADER

AUTHORIZATION_HEADER = "Authorization"
BEARER_SCHEME = "bearer"
API_PREFIX = "/api/"
BEARER_TOKEN_MISSING_DETAIL = "Missing bearer token"
BEARER_TOKEN_INVALID_DETAIL = "Invalid bearer token"
SERVICE_TOKEN_MISSING_DETAIL = "Missing service bearer token"
SERVICE_TOKEN_INVALID_DETAIL = "Invalid service bearer token"
IGNORING_INVALID_BEARER_TOKEN_MESSAGE = "Ignoring invalid bearer token on public path"


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


def collect_service_protected_routes(app: FastAPI) -> list[ProtectedRoute]:
    protected_routes: list[ProtectedRoute] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        if bool(getattr(route.endpoint, "__service_auth_required__", False)):
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
            bool(getattr(dependency.call, "__service_auth_required__", False))
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


def _bind_auth_context(request: Request, user_context: UserContext) -> None:
    request.state.user_context = user_context
    request.state.auth_payload = user_context.claims
    request.state.user_id = user_context.user_id
    request.state.permissions = user_context.permissions
    request.state.roles = user_context.roles
    structlog.contextvars.bind_contextvars(user_id=str(user_context.user_id))


def _bind_service_context(
    request: Request,
    service_context: ServiceContext,
) -> None:
    request.state.service_context = service_context
    request.state.service_name = service_context.service_name
    request.state.service_scopes = service_context.scopes
    structlog.contextvars.bind_contextvars(
        service_name=service_context.service_name,
    )


def _unauthorized(detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": detail},
    )


def _route_matches(
    routes: list[ProtectedRoute],
    path: str,
    method: str,
) -> bool:
    return any(route.matches(path, method) for route in routes)


async def _handle_service_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    service_provider: IServiceProvider | None,
) -> Response:
    if service_provider is None:
        return _unauthorized(SERVICE_TOKEN_INVALID_DETAIL)

    service_token = _extract_bearer_token(
        request.headers.get(SERVICE_AUTHORIZATION_HEADER, "")
    )
    if service_token is None:
        return _unauthorized(SERVICE_TOKEN_MISSING_DETAIL)

    try:
        service_context = service_provider.get_service_context(service_token)
    except TokenError:
        return _unauthorized(SERVICE_TOKEN_INVALID_DETAIL)

    _bind_service_context(request, service_context)
    return await call_next(request)


async def _handle_public_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    user_provider: IUserProvider,
    token: str | None,
) -> Response:
    if token is not None:
        try:
            user_context = user_provider.get_user_context(token)
        except TokenError:
            structlog.get_logger(__name__).warning(
                IGNORING_INVALID_BEARER_TOKEN_MESSAGE,
                path=request.url.path,
            )
        else:
            _bind_auth_context(request, user_context)
    return await call_next(request)


async def _handle_protected_user_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    user_provider: IUserProvider,
    token: str | None,
) -> Response:
    if token is None:
        return _unauthorized(BEARER_TOKEN_MISSING_DETAIL)

    try:
        user_context = user_provider.get_user_context(token)
    except TokenError:
        return _unauthorized(BEARER_TOKEN_INVALID_DETAIL)

    _bind_auth_context(request, user_context)
    return await call_next(request)


def build_jwt_auth_middleware(
    user_provider: IUserProvider,
    protected_routes: list[ProtectedRoute] | None = None,
    service_provider: IServiceProvider | None = None,
    service_protected_routes: list[ProtectedRoute] | None = None,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    routes = protected_routes if protected_routes is not None else []
    service_routes = (
        service_protected_routes if service_protected_routes is not None else []
    )

    async def jwt_auth_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        token = _extract_bearer_token(request.headers.get(AUTHORIZATION_HEADER, ""))
        path = request.url.path
        method = request.method

        if _route_matches(service_routes, path, method):
            return await _handle_service_request(
                request,
                call_next,
                service_provider,
            )

        is_protected = _route_matches(routes, path, method)
        if _is_public_path(path, is_protected):
            return await _handle_public_request(
                request,
                call_next,
                user_provider,
                token,
            )

        return await _handle_protected_user_request(
            request,
            call_next,
            user_provider,
            token,
        )

    return jwt_auth_middleware
