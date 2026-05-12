from src.common.application.security import (
    HasServiceJwtEncodeSettings,
    create_service_token,
)
from src.common.domain.service_auth import SERVICE_AUTHORIZATION_HEADER


def create_service_auth_headers(
    audience: str,
    settings: HasServiceJwtEncodeSettings,
    scopes: list[str] | None = None,
) -> dict[str, str]:
    token = create_service_token(audience, settings, scopes)
    return {SERVICE_AUTHORIZATION_HEADER: f"Bearer {token}"}
