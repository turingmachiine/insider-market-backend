from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide

from src.admin_service.application.dto import (
    AdminDashboardDTO,
    HealthStatusDTO,
    SavedFilterCreateDTO,
    SavedFilterDTO,
)
from src.admin_service.application.usecases import AdminUseCases
from src.admin_service.core.config import AdminSettings, settings
from src.admin_service.infrastructure.di.providers import ContainerProvider
from src.admin_service.main import create_app
from src.common.application.security import encode_jwt
from src.common.domain.security import Permission


class FakeAdminUseCases:
    async def get_dashboard_overview(self) -> AdminDashboardDTO:  # NOSONAR(S7503)
        return AdminDashboardDTO(
            services=[
                HealthStatusDTO(service="auth", status="healthy", version="1.0.0"),
            ],
            event_moderation_queue_size=2,
            users_total=5,
            rating_leaderboard_size=7,
            profiles_total=4,
        )

    async def get_system_health(self) -> list[HealthStatusDTO]:  # NOSONAR(S7503)
        return [
            HealthStatusDTO(service="auth", status="healthy", version="1.0.0"),
            HealthStatusDTO(service="admin", status="healthy", version="1.0.0"),
        ]

    async def save_filter(  # NOSONAR(S7503)
        self, dto: SavedFilterCreateDTO
    ) -> SavedFilterDTO:
        return SavedFilterDTO(
            id=uuid4(),
            actor_user_id=dto.actor_user_id,
            name=dto.name,
            scope=dto.scope,
            criteria=dto.criteria,
            created_at=datetime.now(UTC),
        )


class FakeUseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    @staticmethod
    def provide_admin_use_cases() -> AdminUseCases:
        return FakeAdminUseCases()  # type: ignore[return-value]


def _bearer_token() -> str:
    return encode_jwt(
        {
            "sub": str(uuid4()),
            "permissions": [permission.value for permission in Permission],
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        settings.JWT_SECRET,
        settings.JWT_ALGORITHM,
    )


@pytest_asyncio.fixture
async def admin_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    container = make_async_container(
        ContainerProvider(AdminSettings()),
        FakeUseCaseProvider(),
    )
    app = create_app(container=container)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    await container.close()


@pytest.mark.asyncio
async def test_admin_dashboard_and_filter_flow(admin_client: httpx.AsyncClient) -> None:
    token = _bearer_token()

    dashboard_response = await admin_client.get(
        "/api/v1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["users_total"] == 5

    filter_response = await admin_client.post(
        "/api/v1/saved-filters",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Moderation",
            "scope": "event",
            "criteria": {"status": ["pending"]},
        },
    )
    assert filter_response.status_code == 201
    assert filter_response.json()["name"] == "Moderation"


@pytest.mark.asyncio
async def test_admin_health_is_public(admin_client: httpx.AsyncClient) -> None:
    response = await admin_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
