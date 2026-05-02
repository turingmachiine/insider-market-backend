from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as redis
from fastapi import FastAPI

from src.backend.auth_service.core.config import settings
from src.backend.auth_service.infrastructure.db import (
    create_engine,
    create_session_factory,
)
from src.backend.auth_service.presentation.api.v1.routes import router as v1_router


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
        servers=[
            {"url": f"/{settings.PROXY_NAME}", "description": "Через Gateway"},
            {"url": "", "description": "Локально"},
        ],
    )

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    app.include_router(v1_router, prefix="/api")

    return app


app = create_app()
