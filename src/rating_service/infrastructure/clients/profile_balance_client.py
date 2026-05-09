from decimal import Decimal
from uuid import UUID

import httpx

from src.rating_service.application.ports import ProfileBalancePort


class ProfileBalanceClient(ProfileBalancePort):
    def __init__(self, base_url: str, http_client: httpx.AsyncClient):
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client

    async def credit_achievement_reward(
        self,
        user_id: UUID,
        amount: Decimal,
        achievement_code: str,
        idempotency_key: str,
    ) -> None:
        response = await self.http_client.post(
            f"{self.base_url}/api/profiles/{user_id}/balance/transactions",
            json={
                "transaction_type": "credit",
                "amount": str(amount),
                "source": "rating.achievement_reward",
                "idempotency_key": idempotency_key,
                "metadata": {"achievement_code": achievement_code},
            },
        )
        response.raise_for_status()
