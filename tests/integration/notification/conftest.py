from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio

from src.backend.notification_service.core.config import NotificationSettings
from src.backend.notification_service.infrastructure.di import create_container
from src.backend.notification_service.main import create_app


@pytest_asyncio.fixture(scope="function")
async def notification_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    settings = NotificationSettings(REDIS_URL=None)
    container = create_container(settings)
    app = create_app(container=container)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await container.close()
