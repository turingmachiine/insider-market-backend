from decimal import Decimal
from uuid import UUID

import httpx

from src.auth_service.application.ports import UserProvisioningPort
from src.auth_service.core.config import AuthSettings
from src.common.domain.service_auth import (
    MARKET_SERVICE_AUDIENCE,
    PROFILE_CREATE_SCOPE,
    PROFILE_SERVICE_AUDIENCE,
    WALLET_CREATE_SCOPE,
)
from src.common.infrastructure.integration import create_service_auth_headers


class UserProvisioningClient(UserProvisioningPort):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        settings: AuthSettings,
    ) -> None:
        self._http_client = http_client
        self._settings = settings
        self._profile_base_url = str(settings.PROFILE_SERVICE_URL).rstrip("/")
        self._market_base_url = str(settings.MARKET_SERVICE_URL).rstrip("/")

    async def provision_user(
        self,
        user_id: UUID,
        email: str,
        correlation_id: str | None = None,
    ) -> None:
        display_name = email.split("@", 1)[0] or email
        headers = {"X-Request-ID": correlation_id} if correlation_id else None
        await self._create_profile(user_id, display_name, headers)
        await self._create_wallet(user_id, headers)

    async def _create_profile(
        self,
        user_id: UUID,
        display_name: str,
        headers: dict[str, str] | None,
    ) -> None:
        request_headers = create_service_auth_headers(
            PROFILE_SERVICE_AUDIENCE,
            self._settings,
            [PROFILE_CREATE_SCOPE],
        )
        if headers is not None:
            request_headers.update(headers)
        response = await self._http_client.post(
            f"{self._profile_base_url}/api/v1/internal/profiles",
            json={
                "user_id": str(user_id),
                "display_name": display_name,
                "initial_balance": str(Decimal("1000")),
            },
            headers=request_headers,
        )
        self._raise_for_unexpected_response(response, "profile")

    async def _create_wallet(
        self,
        user_id: UUID,
        headers: dict[str, str] | None,
    ) -> None:
        request_headers = create_service_auth_headers(
            MARKET_SERVICE_AUDIENCE,
            self._settings,
            [WALLET_CREATE_SCOPE],
        )
        if headers is not None:
            request_headers.update(headers)
        response = await self._http_client.post(
            f"{self._market_base_url}/api/v1/internal/wallets",
            json={
                "user_id": str(user_id),
                "initial_balance": str(Decimal("1000")),
            },
            headers=request_headers,
        )
        self._raise_for_unexpected_response(response, "wallet")

    @staticmethod
    def _raise_for_unexpected_response(
        response: httpx.Response,
        target: str,
    ) -> None:
        if response.status_code in {200, 201}:
            return
        raise ValueError(f"Failed to provision user {target}: {response.text}")


__all__ = ["UserProvisioningClient"]
