from decimal import Decimal
from uuid import UUID

import httpx

from src.common.domain.service_auth import (
    PROFILE_BALANCE_WRITE_SCOPE,
    PROFILE_SERVICE_AUDIENCE,
)
from src.common.infrastructure.integration import create_service_auth_headers
from src.rating_service.application.ports import ProfileBalancePort
from src.rating_service.core.config import RatingSettings


class ProfileBalanceClient(ProfileBalancePort):
    def __init__(
        self,
        base_url: str,
        http_client: httpx.AsyncClient,
        settings: RatingSettings,
    ):
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.settings = settings

    async def credit_achievement_reward(
        self,
        user_id: UUID,
        amount: Decimal,
        achievement_code: str,
        idempotency_key: str,
    ) -> None:
        response = await self.http_client.post(
            f"{self.base_url}/api/v1/internal/profiles/{user_id}/balance/transactions",
            headers=create_service_auth_headers(
                PROFILE_SERVICE_AUDIENCE,
                self.settings,
                [PROFILE_BALANCE_WRITE_SCOPE],
            ),
            json={
                "transaction_type": "credit",
                "amount": str(amount),
                "source": "rating.achievement_reward",
                "idempotency_key": idempotency_key,
                "metadata": {"achievement_code": achievement_code},
            },
        )
        response.raise_for_status()
