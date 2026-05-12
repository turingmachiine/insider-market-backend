from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import httpx
import pytest
from fastapi import APIRouter, Depends, FastAPI

from src.common.application.security import encode_jwt
from src.common.application.user_context import UserContext
from src.common.domain.security import Permission
from src.common.infrastructure.integration import JwtUserProvider
from src.common.presentation.decorators import require_permission
from src.common.presentation.middleware import (
    build_jwt_auth_middleware,
    collect_protected_routes,
)

PRIVATE_ENDPOINT_DEPENDENCY = Depends(require_permission(Permission.NSI_READ))


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
        _: UserContext = PRIVATE_ENDPOINT_DEPENDENCY,
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
