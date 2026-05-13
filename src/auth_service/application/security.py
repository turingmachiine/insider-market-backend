import hashlib
import secrets
from typing import cast

from passlib.context import CryptContext

from src.auth_service.application.constants import (
    PASSWORD_HASH_ROUNDS,
    PASSWORD_HASH_SCHEME,
)
from src.common.application.security import (
    TokenError,
    create_access_token,
    decode_access_token,
)

pwd_context = CryptContext(
    schemes=[PASSWORD_HASH_SCHEME],
    deprecated="auto",
    pbkdf2_sha256__rounds=PASSWORD_HASH_ROUNDS,
)


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(password: str, password_hash: str) -> bool:
    return cast(bool, pwd_context.verify(password, password_hash))


def password_hash_needs_update(password_hash: str) -> bool:
    return cast(bool, pwd_context.needs_update(password_hash))


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


__all__ = [
    "TokenError",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "hash_refresh_token",
    "hash_password",
    "password_hash_needs_update",
    "verify_password",
]
