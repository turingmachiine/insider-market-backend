from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from src.auth_service.core.config import settings
from src.auth_service.infrastructure.db.tables import (
    audit_logs_table,
    password_reset_tokens_table,
)
from src.common.application.security import encode_jwt


@pytest.mark.asyncio
async def test_register_login_token(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/register",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    assert response.status_code == 201

    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "user@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    assert "nsi:read" in data["permissions"]


@pytest.mark.asyncio
async def test_register_rejects_weak_password(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/register",
        json={"email": "weak@example.com", "password": "password123"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_auth_events_are_audited(
    auth_client: httpx.AsyncClient,
    auth_engine: AsyncEngine,
) -> None:
    response = await auth_client.post(
        "/api/v1/register",
        json={"email": "audit@example.com", "password": "Password123!"},
        headers={"X-Request-ID": "request-register"},
    )
    assert response.status_code == 201
    user_id = response.json()["user_id"]

    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "audit@example.com", "password": "Password123!"},
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
async def test_password_reset_request_creates_single_use_token(
    auth_client: httpx.AsyncClient,
    auth_engine: AsyncEngine,
) -> None:
    await auth_client.post(
        "/api/v1/register",
        json={"email": "reset-request@example.com", "password": "Password123!"},
    )

    response = await auth_client.post(
        "/api/v1/password/reset/request",
        json={"email": "reset-request@example.com"},
    )
    assert response.status_code == 204
    assert not response.content

    async with auth_engine.connect() as conn:
        result = await conn.execute(select(password_reset_tokens_table.c.token_hash))
        rows = result.mappings().all()
    assert len(rows) == 1
    assert rows[0]["token_hash"]


@pytest.mark.asyncio
async def test_change_password_revokes_refresh_token(
    auth_client: httpx.AsyncClient,
) -> None:
    await auth_client.post(
        "/api/v1/register",
        json={"email": "change@example.com", "password": "Password123!"},
    )
    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "change@example.com", "password": "Password123!"},
    )
    data = response.json()

    response = await auth_client.post(
        "/api/v1/password/change",
        json={
            "current_password": "Password123!",
            "new_password": "ChangedPassword123!",
        },
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert response.status_code == 204

    response = await auth_client.post(
        "/api/v1/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert response.status_code == 401

    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "change@example.com", "password": "ChangedPassword123!"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_rotates_token(auth_client: httpx.AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/register",
        json={"email": "refresh@example.com", "password": "Password123!"},
    )
    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "refresh@example.com", "password": "Password123!"},
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
        json={"email": "logout@example.com", "password": "Password123!"},
    )
    response = await auth_client.post(
        "/api/v1/login",
        json={"email": "logout@example.com", "password": "Password123!"},
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
