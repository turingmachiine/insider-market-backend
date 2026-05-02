from typing import Annotated, AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.backend.auth_service.application.repository import AuthRepository
from src.backend.auth_service.application.service import AuthError, AuthService
from src.backend.auth_service.core.config import settings
from src.backend.auth_service.infrastructure.cache.permissions_cache import (
    PermissionsCache,
)
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


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[
        AsyncSession
    ] = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_auth_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    cache = PermissionsCache(
        request.app.state.redis,
        ttl_seconds=settings.PERMISSIONS_CACHE_TTL,
    )
    return AuthService(AuthRepository(session), cache, settings)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisterResponse:
    try:
        user_id = await auth_service.register(request.email, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return RegisterResponse(user_id=user_id)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
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
async def get_my_permissions(
    payload: Annotated[
        dict[str, object],
        Depends(require_permission("nsi:read", settings)),
    ],
) -> dict[str, object]:
    return {
        "user_id": payload["sub"],
        "permissions": payload.get("permissions", []),
    }
