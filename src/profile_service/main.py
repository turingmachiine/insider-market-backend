from contextlib import asynccontextmanager
from typing import AsyncIterator, cast

import structlog
from dishka.integrations.fastapi import AsyncContainer, setup_dishka
from fastapi import FastAPI

from src.common.logging import RequestContextMiddleware, setup_logging, shutdown_logging
from src.common.presentation.middleware import (
    build_jwt_auth_middleware,
    collect_protected_routes,
)
from src.profile_service.core.config import settings
from src.profile_service.infrastructure.db import setup_mapping
from src.profile_service.infrastructure.di import create_container
from src.profile_service.presentation.api.v1.routes import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log_broker_url = (
        settings.LOG_REDIS_URL or settings.REDIS_URL
        if settings.LOG_BROKER_ENABLED
        else None
    )
    setup_logging(
        service_name="profile_service",
        json_logs=settings.JSON_LOGS,
        log_level=settings.LOG_LEVEL,
        broker_url=log_broker_url,
        broker_key=settings.LOG_REDIS_KEY,
    )
    logger = structlog.get_logger("profile_service")
    logger.info("Starting Profile Service", version=settings.APP_VERSION)
    yield
    logger.info("Shutting down Profile Service")
    container = cast(AsyncContainer, app.state.dishka_container)
    await container.close()
    shutdown_logging()


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    setup_mapping()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        servers=[
            {"url": f"/{settings.PROXY_NAME}", "description": "Через Gateway"},
            {"url": "", "description": "Локально"},
        ],
    )
    protected_routes: list = []
    app.middleware("http")(build_jwt_auth_middleware(settings, protected_routes))
    app.add_middleware(RequestContextMiddleware)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    app.include_router(v1_router, prefix="/api")
    protected_routes.extend(collect_protected_routes(app))

    if container is None:
        container = create_container(settings)
    setup_dishka(container, app)

    return app


app = create_app()
