from typing import cast

from passlib.context import CryptContext

from src.common.application.security import (
    TokenError,
    create_access_token,
    decode_access_token,
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(password: str, password_hash: str) -> bool:
    return cast(bool, pwd_context.verify(password, password_hash))


__all__ = [
    "TokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
