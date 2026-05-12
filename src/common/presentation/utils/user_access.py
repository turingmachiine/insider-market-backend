from uuid import UUID

from fastapi import HTTPException, status

from src.common.application.user_context import UserContext
from src.common.domain.security import Permission


def can_access_user_resource(
    user_context: UserContext,
    owner_user_id: UUID,
    elevated_permission: Permission | str,
) -> bool:
    return user_context.user_id == owner_user_id or user_context.has_permission(
        elevated_permission
    )


def require_user_owner(
    user_context: UserContext,
    owner_user_id: UUID,
    detail: str,
) -> None:
    if user_context.user_id != owner_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
