from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from src.common.domain.security import normalize_permission


class TokenError(ValueError):
    pass


class HasJwtDecodeSettings(Protocol):
    JWT_SECRET: str
    JWT_ALGORITHM: str


class HasJwtEncodeSettings(HasJwtDecodeSettings, Protocol):
    JWT_TTL: int


class HasServiceJwtDecodeSettings(Protocol):
    SERVICE_JWT_SECRET: str
    SERVICE_JWT_ALGORITHM: str
    SERVICE_NAME: str


class HasServiceJwtEncodeSettings(HasServiceJwtDecodeSettings, Protocol):
    SERVICE_JWT_TTL: int


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _json_dumps(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8",
    )


def encode_jwt(payload: dict[str, Any], secret: str, algorithm: str = "HS256") -> str:
    if algorithm != "HS256":
        raise TokenError("Unsupported JWT algorithm")

    header = {"alg": algorithm, "typ": "JWT"}
    signing_input = ".".join(
        (
            _b64url_encode(_json_dumps(header)),
            _b64url_encode(_json_dumps(payload)),
        )
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_jwt(token: str, secret: str, algorithm: str = "HS256") -> dict[str, Any]:
    if algorithm != "HS256":
        raise TokenError("Unsupported JWT algorithm")
    invalid_token_msg = "Invalid token"
    parts = token.split(".")
    if len(parts) != 3:
        raise TokenError(invalid_token_msg)

    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    try:
        actual_signature = _b64url_decode(parts[2])
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except ValueError as exc:
        raise TokenError(invalid_token_msg) from exc

    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise TokenError(invalid_token_msg)
    if header.get("alg") != algorithm:
        raise TokenError("Invalid token algorithm")
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise TokenError("Invalid token signature")

    return payload


def create_access_token(
    user_id: UUID,
    permissions: list[str],
    settings: HasJwtEncodeSettings,
    roles: list[str] | None = None,
) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(seconds=settings.JWT_TTL)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "permissions": [normalize_permission(permission) for permission in permissions],
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if roles is not None:
        payload["roles"] = roles
    return encode_jwt(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)


def decode_access_token(
    token: str,
    settings: HasJwtDecodeSettings,
) -> dict[str, Any]:
    payload = decode_jwt(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)

    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        raise TokenError("Invalid token expiration")
    if datetime.now(UTC).timestamp() > float(exp):
        raise TokenError("Token expired")
    if not payload.get("sub"):
        raise TokenError("Invalid token subject")
    return payload


def create_service_token(
    audience: str,
    settings: HasServiceJwtEncodeSettings,
    scopes: list[str] | None = None,
) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(seconds=settings.SERVICE_JWT_TTL)
    payload: dict[str, Any] = {
        "token_use": "service",
        "sub": settings.SERVICE_NAME,
        "aud": audience,
        "scopes": scopes or [],
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return encode_jwt(
        payload,
        settings.SERVICE_JWT_SECRET,
        settings.SERVICE_JWT_ALGORITHM,
    )


def decode_service_token(
    token: str,
    settings: HasServiceJwtDecodeSettings,
) -> dict[str, Any]:
    payload = decode_jwt(
        token,
        settings.SERVICE_JWT_SECRET,
        settings.SERVICE_JWT_ALGORITHM,
    )

    if payload.get("token_use") != "service":
        raise TokenError("Invalid service token type")

    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        raise TokenError("Invalid token expiration")
    if datetime.now(UTC).timestamp() > float(exp):
        raise TokenError("Token expired")

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise TokenError("Invalid service token subject")

    if payload.get("aud") != settings.SERVICE_NAME:
        raise TokenError("Invalid service token audience")

    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list) or not all(
        isinstance(scope, str) for scope in scopes
    ):
        raise TokenError("Invalid service token scopes")

    return payload
