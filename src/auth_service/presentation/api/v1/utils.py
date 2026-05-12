from datetime import datetime

from src.auth_service.domain.entities import User
from src.auth_service.presentation.api.v1.schemas import UserResponse


def to_user_response(user: User) -> UserResponse:
    created_at = getattr(user, "created_at", None)
    if not isinstance(created_at, datetime):
        created_at = None
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        roles=[role.name for role in user.roles],
        permissions=sorted(
            {permission.name for role in user.roles for permission in role.permissions}
        ),
        created_at=created_at,
    )
