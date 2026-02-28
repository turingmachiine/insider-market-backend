"""Точка входа приложения FastAPI"""

import logging.config
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka.integrations.fastapi import AsyncContainer, setup_dishka
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from src.core.config import settings
from src.infrastructure.db import setup_mapping
from src.infrastructure.di import create_container
from src.infrastructure.logging.config import setup_logging
from src.presentation.api.v1.routes import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """LifeSpan контекст менеджера приложения"""
    # Startup
    setup_mapping()
    setup_logging(json_logs=settings.JSON_LOGS, log_level=settings.LOG_LEVEL)
    logger = logging.getLogger("football_research")
    logger.info(
        "Starting Football Research API", extra={"version": settings.APP_VERSION}
    )

    yield

    # Shutdown
    logger = logging.getLogger("football_research")
    logger.info("Shutting down Football Research API")
    await app.state.dishka_container.close()  # noqa


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
    )

    # Swagger UI
    @app.get("/api/docs", response_class=HTMLResponse, include_in_schema=False)
    async def get_docs() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - Swagger",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        )

    # ReDoc
    @app.get("/api/redoc", response_class=HTMLResponse, include_in_schema=False)
    async def get_redoc() -> HTMLResponse:
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{settings.APP_NAME} - ReDoc",
        )

    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.APP_VERSION}

    # Подключение роутеров (префикс /api/v1 уже есть в router)
    app.include_router(v1_router, prefix="/api")

    if container is None:
        container = create_container(settings)
    setup_dishka(container, app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
    )
