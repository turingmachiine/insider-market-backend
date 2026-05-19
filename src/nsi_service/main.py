"""Точка входа приложения FastAPI"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from dishka.integrations.fastapi import AsyncContainer, setup_dishka
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from src.common.infrastructure.integration import JwtUserProvider
from src.common.logging import RequestContextMiddleware, shutdown_logging
from src.common.presentation import register_exception_handlers
from src.common.presentation.middleware import (
    build_jwt_auth_middleware,
    collect_protected_routes,
)
from src.nsi_service.core.config import settings
from src.nsi_service.infrastructure.db import setup_mapping
from src.nsi_service.infrastructure.di import create_container
from src.nsi_service.infrastructure.logging.config import setup_logging
from src.nsi_service.presentation.api.v1.routes import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """LifeSpan контекст менеджера приложения"""
    # Startup
    setup_mapping()
    log_broker_url = (
        settings.LOG_REDIS_URL or settings.REDIS_URL
        if settings.LOG_BROKER_ENABLED
        else None
    )
    setup_logging(
        json_logs=settings.JSON_LOGS,
        log_level=settings.LOG_LEVEL,
        broker_url=log_broker_url,
        broker_key=settings.LOG_REDIS_KEY,
    )
    logger = structlog.get_logger("insider_market_backend")
    logger.info(
        "Starting Football Research Insider Market", version=settings.APP_VERSION
    )

    yield

    # Shutdown
    logger.info("Shutting down Football Research Insider Market")
    await app.state.dishka_container.close()  # noqa
    shutdown_logging()


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    """Создание приложения FastAPI"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Football research application with clean architecture for "
            "player analysis, radar charts, similar player matching, "
            "and shadow-team formation."
        ),
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
        servers=[
            {"url": f"/{settings.PROXY_NAME}", "description": "Через Gateway"},
            {"url": "", "description": "Локально"},
        ],
    )
    register_exception_handlers(app)

    protected_routes: list = []
    app.middleware("http")(
        build_jwt_auth_middleware(JwtUserProvider(settings), protected_routes)
    )
    app.add_middleware(RequestContextMiddleware)

    # Swagger UI
    @app.get("/api/docs", response_class=HTMLResponse, include_in_schema=False)
    def get_docs() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - Swagger",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        )

    # ReDoc
    @app.get("/api/redoc", response_class=HTMLResponse, include_in_schema=False)
    def get_redoc() -> HTMLResponse:
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - ReDoc",
        )

    # Health check
    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    # Подключение роутеров (префикс /api/v1 уже есть в router)
    app.include_router(v1_router, prefix="/api")
    protected_routes.extend(collect_protected_routes(app))

    if container is None:
        container = create_container(settings)
    setup_dishka(container, app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.nsi_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )
