from datetime import UTC, datetime, timedelta

import httpx
import pytest
from jose import jwt
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from src.backend.auth_service.core.config import settings
from src.backend.auth_service.infrastructure.db.database import create_session_factory
from src.backend.auth_service.infrastructure.db.models import Base
from src.backend.auth_service.main import create_app


@pytest.fixture
def auth_postgres_container() -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture
async def auth_client(auth_postgres_container: PostgresContainer):
    db_url = auth_postgres_container.get_connection_url().replace(
        "postgresql://",
        "postgresql+asyncpg://",
    )
    settings.DATABASE_URL_AUTH = db_url
    settings.REDIS_URL = None
    settings.JWT_SECRET = "test-secret"
    settings.JWT_TTL = 3600

    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = None
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_login_token(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.post(
        "/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 201

    response = await auth_client.post(
        "/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert "nsi:read" in data["permissions"]


@pytest.mark.asyncio
async def test_invalid_token_rejected(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get(
        "/permissions/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejected(auth_client: httpx.AsyncClient) -> None:
    token = jwt.encode(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "permissions": ["nsi:read"],
            "exp": datetime.now(UTC) - timedelta(seconds=1),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = await auth_client.get(
        "/permissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_permission_required_not_role(auth_client: httpx.AsyncClient) -> None:
    token = jwt.encode(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "permissions": ["other:permission"],
            "roles": ["admin"],
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = await auth_client.get(
        "/permissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
