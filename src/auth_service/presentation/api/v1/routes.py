from datetime import datetime
from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth_service.application.service import AuthError, AuthService
from src.auth_service.core.config import AuthSettings
from src.auth_service.domain.entities import User
from src.auth_service.presentation.api.v1.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserListResponse,
    UserResponse,
    UserRoleGrantRequest,
    UserStatusUpdateRequest,
)
from src.common.domain.security import Permission
from src.common.presentation.decorators import require_permission

router = APIRouter(prefix="/v1")


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register(
    request: RegisterRequest,
    auth_service: FromDishka[AuthService],
) -> RegisterResponse:
    try:
        user_id = await auth_service.register(request.email, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return RegisterResponse(user_id=user_id)


@router.post("/login")
@inject
async def login(
    request: LoginRequest,
    auth_service: FromDishka[AuthService],
    settings: FromDishka[AuthSettings],
) -> TokenResponse:
    try:
        token, user_id, permissions = await auth_service.login(
            request.email,
            request.password,
        )
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_TTL,
        user_id=user_id,
        permissions=permissions,
    )


@router.get("/users")
@inject
async def list_users(
    auth_service: FromDishka[AuthService],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.AUTH_USERS_READ))
    ],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserListResponse:
    users = await auth_service.list_users(limit=limit, offset=offset)
    total = await auth_service.count_users()
    return UserListResponse(
        items=[_to_user_response(user) for user in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/users/{user_id}")
@inject
async def get_user(
    user_id: UUID,
    auth_service: FromDishka[AuthService],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.AUTH_USERS_READ))
    ],
) -> UserResponse:
    user = await auth_service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return _to_user_response(user)


@router.get("/users/{user_id}/permissions")
@inject
async def get_user_permissions(
    user_id: UUID,
    auth_service: FromDishka[AuthService],
    _: Annotated[
        dict[str, object],
        Depends(require_permission(Permission.AUTH_PERMISSIONS_READ)),
    ],
) -> dict[str, object]:
    try:
        permissions = await auth_service.get_permissions(user_id)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return {"user_id": str(user_id), "permissions": permissions}


@router.patch("/users/{user_id}/status")
@inject
async def set_user_status(
    user_id: UUID,
    request: UserStatusUpdateRequest,
    auth_service: FromDishka[AuthService],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.AUTH_USERS_WRITE))
    ],
) -> UserResponse:
    user = await auth_service.set_user_status(user_id, request.is_active)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return _to_user_response(user)


@router.post("/users/{user_id}/roles")
@inject
async def assign_role(
    user_id: UUID,
    request: UserRoleGrantRequest,
    auth_service: FromDishka[AuthService],
    _: Annotated[
        dict[str, object], Depends(require_permission(Permission.AUTH_ROLES_WRITE))
    ],
) -> UserResponse:
    user = await auth_service.assign_role(
        user_id=user_id,
        role_name=request.role_name,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {str(user_id)} not found",
        )
    return _to_user_response(user)


@router.get("/permissions/me")
def get_my_permissions(
    payload: Annotated[
        dict[str, object],
        Depends(require_permission(Permission.AUTH_PERMISSIONS_READ)),
    ],
) -> dict[str, object]:
    return {
        "user_id": payload["sub"],
        "permissions": payload.get("permissions", []),
    }


def _to_user_response(user: User) -> UserResponse:
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
