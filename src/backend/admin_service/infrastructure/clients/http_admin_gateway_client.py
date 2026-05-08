from typing import Any, cast
from uuid import UUID

import httpx

from src.backend.admin_service.application.ports import AdminGatewayClient
from src.backend.admin_service.core.config import AdminSettings


class HttpAdminGatewayClient(AdminGatewayClient):
    def __init__(
        self,
        settings: AdminSettings,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._settings = settings
        self._http_client = http_client

    def _base(self, service: str) -> str:
        mapping = {
            "auth": str(self._settings.SERVICE_AUTH_URL),
            "event": str(self._settings.SERVICE_EVENT_URL),
            "profile": str(self._settings.SERVICE_PROFILE_URL),
            "rating": str(self._settings.SERVICE_RATING_URL),
            "market": str(self._settings.SERVICE_MARKET_URL),
            "rumor": str(self._settings.SERVICE_RUMOR_URL),
            "nsi": str(self._settings.SERVICE_NSI_URL),
        }
        return mapping[service].rstrip("/")

    async def get_health(self, service: str) -> dict:
        response = await self._http_client.get(f"{self._base(service)}/health")
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_event_moderation_queue(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        response = await self._http_client.get(
            f"{self._base('event')}/api/v1/events/moderation-queue",
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def call_event_action(
        self,
        event_id: UUID,
        action: str,
        payload: dict | None = None,
    ) -> dict:
        response = await self._http_client.post(
            f"{self._base('event')}/api/v1/events/{event_id}/{action}",
            json=payload or {},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def list_users(self, limit: int = 100, offset: int = 0) -> dict:
        response = await self._http_client.get(
            f"{self._base('auth')}/api/v1/users",
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_user(self, user_id: UUID) -> dict:
        response = await self._http_client.get(
            f"{self._base('auth')}/api/v1/users/{user_id}",
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_user_permissions(self, user_id: UUID) -> dict:
        response = await self._http_client.get(
            f"{self._base('auth')}/api/v1/users/{user_id}/permissions",
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def set_user_status(self, user_id: UUID, is_active: bool) -> dict:
        response = await self._http_client.patch(
            f"{self._base('auth')}/api/v1/users/{user_id}/status",
            json={"is_active": is_active},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def assign_role(
        self,
        user_id: UUID,
        role_name: str,
        permissions: list[str],
    ) -> dict:
        response = await self._http_client.post(
            f"{self._base('auth')}/api/v1/users/{user_id}/roles",
            json={"role_name": role_name, "permissions": permissions},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_profile(self, user_id: UUID) -> dict:
        response = await self._http_client.get(
            f"{self._base('profile')}/api/v1/profiles/{user_id}",
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_rating_profile(self, user_id: UUID) -> dict:
        response = await self._http_client.get(
            f"{self._base('rating')}/api/v1/ratings/profiles/{user_id}",
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def get_rating_leaderboard(self, limit: int = 10) -> dict:
        response = await self._http_client.get(
            f"{self._base('rating')}/api/v1/ratings/leaderboard",
            params={"limit": limit},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    async def list_profiles(self, limit: int = 100, offset: int = 0) -> dict:
        response = await self._http_client.get(
            f"{self._base('profile')}/api/v1/profiles",
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
