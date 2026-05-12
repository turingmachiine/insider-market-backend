from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import UUID, uuid4

import pytest

from src.admin_service.core.config import settings
from src.common.application.security import encode_jwt
from src.common.domain.security import Permission


class TokenFactory(Protocol):
    def __call__(
        self,
        user_id: UUID,
        permissions: list[Permission | str] | None = None,
    ) -> str:
        """Тестовый TokenFactory протокол"""
        pass


@pytest.fixture
def authenticated_user_id() -> UUID:
    return uuid4()


@pytest.fixture
def token_factory() -> TokenFactory:
    def factory(
        user_id: UUID,
        permissions: list[Permission | str] | None = None,
    ) -> str:
        selected_permissions = (
            permissions if permissions is not None else list(Permission)
        )
        return encode_jwt(
            {
                "sub": str(user_id),
                "permissions": [
                    (
                        permission.value
                        if isinstance(permission, Permission)
                        else permission
                    )
                    for permission in selected_permissions
                ],
                "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
            },
            settings.JWT_SECRET,
            settings.JWT_ALGORITHM,
        )

    return factory


@pytest.fixture
def test_token(
    authenticated_user_id: UUID,
    token_factory: TokenFactory,
) -> str:
    return token_factory(authenticated_user_id)
