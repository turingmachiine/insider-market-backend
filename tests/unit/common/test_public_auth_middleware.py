from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Annotated

import httpx
import pytest
from fastapi import APIRouter, Depends, FastAPI

from src.common.application.security import encode_jwt
from src.common.application.service_context import ServiceContext
from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.domain.service_auth import SERVICE_AUTHORIZATION_HEADER
from src.common.infrastructure.integration import JwtServiceProvider, JwtUserProvider
from src.common.presentation.decorators import require_permission, require_service_auth
from src.common.presentation.middleware import (
    build_jwt_auth_middleware,
    collect_protected_routes,
    collect_service_protected_routes,
)

PrivateEndpointContext = Annotated[
    UserContext,
    Depends(require_permission(Permission.NSI_READ)),
]
InternalServiceContext = Annotated[
    ServiceContext,
    Depends(require_service_auth("profile:balance:write")),
]


@pytest.mark.asyncio
async def test_public_routes_stay_open_and_protected_routes_require_auth() -> None:
    app = FastAPI()
    protected_routes: list = []
    settings = SimpleNamespace(JWT_SECRET="secret", JWT_ALGORITHM="HS256")

    app.middleware("http")(
        build_jwt_auth_middleware(JwtUserProvider(settings), protected_routes)
    )

    router = APIRouter(prefix="/api/v1")

    @router.get("/public")
    async def public_endpoint() -> dict[str, str]:
        return {"status": "public"}

    @router.get("/private")
    async def private_endpoint(
        _: PrivateEndpointContext,
    ) -> dict[str, str]:
        return {"status": "private"}

    app.include_router(router)
    protected_routes.extend(collect_protected_routes(app))

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        public_response = await client.get("/api/v1/public")
        assert public_response.status_code == 200

        private_response = await client.get("/api/v1/private")
        assert private_response.status_code == 401

        token = encode_jwt(
            {
                "sub": "00000000-0000-0000-0000-000000000001",
                "permissions": [Permission.NSI_READ.value],
                "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
            },
            settings.JWT_SECRET,
            settings.JWT_ALGORITHM,
        )
        authed_response = await client.get(
            "/api/v1/private",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert authed_response.status_code == 200


@pytest.mark.asyncio
async def test_service_routes_require_service_token_and_reject_user_token() -> None:
    app = FastAPI()
    protected_routes: list = []
    service_protected_routes: list = []
    settings = SimpleNamespace(
        JWT_SECRET="user-secret",
        JWT_ALGORITHM="HS256",
        SERVICE_NAME="profile_service",
        SERVICE_JWT_SECRET="service-secret",
        SERVICE_JWT_ALGORITHM="HS256",
        SERVICE_JWT_TTL=300,
    )

    app.middleware("http")(
        build_jwt_auth_middleware(
            JwtUserProvider(settings),
            protected_routes,
            JwtServiceProvider(settings),
            service_protected_routes,
        )
    )

    router = APIRouter(prefix="/api/v1")

    @router.post("/internal/reward")
    async def internal_endpoint(
        service_context: InternalServiceContext,
    ) -> dict[str, str]:
        return {"service": service_context.service_name}

    app.include_router(router)
    protected_routes.extend(collect_protected_routes(app))
    service_protected_routes.extend(collect_service_protected_routes(app))

    user_token = encode_jwt(
        {
            "sub": "00000000-0000-0000-0000-000000000001",
            "permissions": [Permission.PROFILE_WRITE.value],
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )
    service_token = encode_jwt(
        {
            "token_use": "service",
            "sub": "rating_service",
            "aud": "profile_service",
            "scopes": ["profile:balance:write"],
            "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
        },
        settings.SERVICE_JWT_SECRET,
        settings.SERVICE_JWT_ALGORITHM,
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        missing_response = await client.post("/api/v1/internal/reward")
        assert missing_response.status_code == 401

        user_response = await client.post(
            "/api/v1/internal/reward",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert user_response.status_code == 401

        service_response = await client.post(
            "/api/v1/internal/reward",
            headers={SERVICE_AUTHORIZATION_HEADER: f"Bearer {service_token}"},
        )
        assert service_response.status_code == 200
        assert service_response.json() == {"service": "rating_service"}
