from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import httpx
import pytest_asyncio

from src.common.application.security import encode_jwt
from src.common.domain.security import Permission
from src.notification_service.core.config import NotificationSettings
from src.notification_service.infrastructure.di import create_container
from src.notification_service.main import create_app


@pytest_asyncio.fixture(scope="function")
async def notification_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    settings = NotificationSettings(REDIS_URL=None)
    container = create_container(settings)
    app = create_app(container=container)
    token = encode_jwt(
        {
            "sub": "00000000-0000-0000-0000-000000000001",
            "permissions": [permission.value for permission in Permission],
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client

    await container.close()
