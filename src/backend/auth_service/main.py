from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.backend.auth_service.application.repository import AuthRepository
from src.backend.auth_service.application.service import AuthError, AuthService
from src.backend.auth_service.core.config import settings
from src.backend.auth_service.infrastructure.cache.permissions_cache import (
    PermissionsCache,
)
from src.backend.auth_service.infrastructure.db import (
    create_engine,
    create_session_factory,
)
from src.backend.auth_service.presentation.api.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.backend.auth_service.presentation.middleware.permissions import (
    require_permission,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
    app.state.session_factory = session_factory
    app.state.redis = redis_client
    yield
    if redis_client is not None:
        await redis_client.aclose()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

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

    async def get_auth_service(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> AuthService:
        cache = PermissionsCache(
            request.app.state.redis,
            ttl_seconds=settings.PERMISSIONS_CACHE_TTL,
        )
        return AuthService(AuthRepository(session), cache, settings)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    @app.post(
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

    @app.post("/login", response_model=TokenResponse)
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

    @app.get("/permissions/me")
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

    return app


app = create_app()
