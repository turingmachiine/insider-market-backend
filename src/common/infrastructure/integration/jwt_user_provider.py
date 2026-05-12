from typing import Any
from uuid import UUID

from src.common.application.security import (
    HasJwtDecodeSettings,
    TokenError,
    decode_access_token,
)
from src.common.application.user_context import UserContext


class JwtUserProvider:
    def __init__(self, settings: HasJwtDecodeSettings) -> None:
        self._settings = settings

    def get_user_context(self, token: str) -> UserContext:
        claims = decode_access_token(token, self._settings)
        subject = claims.get("sub")
        try:
            user_id = UUID(str(subject))
        except (TypeError, ValueError) as exc:
            raise TokenError("Invalid token subject") from exc

        return UserContext(
            user_id=user_id,
            subject=str(subject),
            permissions=frozenset(self._extract_strings(claims.get("permissions", []))),
            roles=frozenset(self._extract_strings(claims.get("roles", []))),
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
