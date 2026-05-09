from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.auth_service.core.config import AuthSettings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class TokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(password: str, password_hash: str) -> bool:
    return cast(bool, pwd_context.verify(password, password_hash))


def create_access_token(
    user_id: UUID,
    permissions: list[str],
    settings: AuthSettings,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(seconds=settings.JWT_TTL)
    payload = {
        "sub": str(user_id),
        "permissions": permissions,
        "exp": expires_at,
    }
    return cast(
        str,
        jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM),
    )


def decode_access_token(token: str, settings: AuthSettings) -> dict[str, Any]:
    try:
        payload = cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            ),
        )
    except JWTError as exc:
        raise TokenError("Invalid token") from exc
    if not payload.get("sub"):
        raise TokenError("Invalid token subject")
    return payload
