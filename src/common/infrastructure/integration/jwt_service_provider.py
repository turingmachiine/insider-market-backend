from typing import Any

from src.common.application.security import (
    HasServiceJwtDecodeSettings,
    TokenError,
    decode_service_token,
)
from src.common.application.service_context import ServiceContext


class JwtServiceProvider:
    def __init__(self, settings: HasServiceJwtDecodeSettings) -> None:
        self._settings = settings

    def get_service_context(self, token: str) -> ServiceContext:
        claims = decode_service_token(token, self._settings)
        subject = claims.get("sub")
        audience = claims.get("aud")
        if not isinstance(subject, str) or not isinstance(audience, str):
            raise TokenError("Invalid service token identity")

        return ServiceContext(
            service_name=subject,
            audience=audience,
            scopes=frozenset(self._extract_strings(claims.get("scopes", []))),
            expires_at=self._extract_expiration(claims.get("exp")),
            claims=claims,
        )

    @staticmethod
    def _extract_strings(value: Any) -> set[str]:
        if not isinstance(value, list):
            return set()
        if not all(isinstance(item, str) for item in value):
            return set()
        return set(value)

    @staticmethod
    def _extract_expiration(value: Any) -> int | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return int(value)
