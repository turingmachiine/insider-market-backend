from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.backend.auth_service.application.service import AuthError, AuthService
from src.backend.auth_service.core.config import AuthSettings
from src.backend.auth_service.presentation.api.v1.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.backend.auth_service.presentation.middleware.permissions import (
    require_permission,
)

router = APIRouter(prefix="/v1")


@router.post(
    "/register",
    response_model=RegisterResponse,
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


@router.post("/login", response_model=TokenResponse)
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


@router.get("/permissions/me")
def get_my_permissions(
    payload: Annotated[
        dict[str, object],
        Depends(require_permission("nsi:read")),
    ],
) -> dict[str, object]:
    return {
        "user_id": payload["sub"],
        "permissions": payload.get("permissions", []),
    }
