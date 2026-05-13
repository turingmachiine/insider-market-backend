from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from src.auth_service.core.config import settings
from src.auth_service.infrastructure.db.tables import audit_logs_table
from src.common.application.security import encode_jwt


@pytest.mark.asyncio
async def test_register_login_token(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 201

    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    assert "nsi:read" in data["permissions"]


@pytest.mark.asyncio
async def test_auth_events_are_audited(
    auth_client: httpx.AsyncClient,
    auth_engine: AsyncEngine,
) -> None:
    response = await auth_client.post(
        "/api/v1/register",
        json={"email": "audit@example.com", "password": "password123"},
        headers={"X-Request-ID": "request-register"},
    )
    assert response.status_code == 201
    user_id = response.json()["user_id"]

    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "audit@example.com", "password": "password123"},
        headers={"X-Request-ID": "request-login"},
    )
    assert response.status_code == 200

    async with auth_engine.connect() as conn:
        result = await conn.execute(
            select(
                audit_logs_table.c.action,
                audit_logs_table.c.target_id,
                audit_logs_table.c.actor_user_id,
                audit_logs_table.c.correlation_id,
            ).order_by(audit_logs_table.c.created_at)
        )
        rows = result.mappings().all()

    assert [row["action"] for row in rows[-2:]] == ["register", "login"]
    assert rows[-2]["target_id"] == user_id
    assert rows[-2]["correlation_id"] == "request-register"
    assert str(rows[-1]["actor_user_id"]) == user_id
    assert rows[-1]["correlation_id"] == "request-login"


@pytest.mark.asyncio
async def test_refresh_rotates_token(auth_client: httpx.AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/register",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    refresh_token = response.json()["refresh_token"]

    response = await auth_client.post(
        "/api/v1/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"] != refresh_token

    response = await auth_client.post(
        "/api/v1/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(auth_client: httpx.AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/register",
        json={"email": "logout@example.com", "password": "password123"},
    )
    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "logout@example.com", "password": "password123"},
    )
    refresh_token = response.json()["refresh_token"]

    response = await auth_client.post(
        "/api/v1/logout",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 204

    response = await auth_client.post(
        "/api/v1/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_rejected(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get(
        "/api/v1/permissions/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejected(auth_client: httpx.AsyncClient) -> None:
    token = encode_jwt(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "permissions": ["nsi:read"],
            "exp": int((datetime.now(UTC) - timedelta(seconds=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )

    response = await auth_client.get(
        "/api/v1/permissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_permission_required_not_role(auth_client: httpx.AsyncClient) -> None:
    token = encode_jwt(
        {
            "sub": "00000000-0000-0000-0000-000000000000",
            "permissions": ["other:permission"],
            "roles": ["admin"],
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )

    response = await auth_client.get(
        "/api/v1/permissions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
