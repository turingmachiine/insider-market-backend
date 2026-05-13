from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
import redis.asyncio as redis
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api_gateway.config import GatewaySettings, get_settings
from src.api_gateway.middleware.logging import JsonAccessLogMiddleware
from src.api_gateway.middleware.rate_limit import (
    RateLimitMiddleware,
    WebSocketRateLimitMiddleware,
)
from src.api_gateway.middleware.security import GatewaySecurityMiddleware
from src.api_gateway.presentation.swagger_page import SwaggerLandingPage
from src.api_gateway.routes import router
from src.api_gateway.services.cache import GatewayCache
from src.api_gateway.services.headers import HeaderPolicy
from src.api_gateway.services.openapi import OpenAPIAggregator
from src.api_gateway.services.proxy import UpstreamProxy
from src.api_gateway.services.service_registry import ServiceRegistry
from src.common.logging import RequestContextMiddleware, setup_logging, shutdown_logging


class GatewayApplicationFactory:
    def __init__(
        self,
        settings: GatewaySettings,
        *,
        redis_client: redis.Redis | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._redis_client = redis_client
        self._http_client = http_client
        self._swagger_page = SwaggerLandingPage()

    def create(self) -> FastAPI:
        log_broker_url = (
            self._settings.LOG_REDIS_URL or self._settings.REDIS_URL
            if self._settings.LOG_BROKER_ENABLED
            else None
        )
        setup_logging(
            service_name="api_gateway",
            json_logs=self._settings.JSON_LOGS,
            log_level=self._settings.LOG_LEVEL,
            broker_url=log_broker_url,
            broker_key=self._settings.LOG_REDIS_KEY,
        )
        app = FastAPI(
            title=self._settings.APP_NAME,
            version=self._settings.APP_VERSION,
            docs_url=None,
            redoc_url=None,
            lifespan=self._lifespan,
        )
        self._configure_state(app)
        self._configure_static_assets(app)
        self._configure_middleware(app)
        app.include_router(router)
        return app

    def _configure_state(self, app: FastAPI) -> None:
        app.state.settings = self._settings
        app.state.redis = self._redis_client
        app.state.http_client = self._http_client
        app.state.owns_redis = False
        app.state.owns_http_client = False
        app.state.swagger_page = self._swagger_page
        self._configure_gateway_services(app)

    def _configure_static_assets(self, app: FastAPI) -> None:
        app.mount(
            "/swagger/assets",
            StaticFiles(directory=self._swagger_page.resource_paths.static_root),
            name="swagger-assets",
        )
        app.mount(
            "/docs/assets",
            StaticFiles(directory=self._swagger_page.resource_paths.static_root),
            name="docs-assets",
        )

    def _configure_middleware(self, app: FastAPI) -> None:
        app.add_middleware(
            WebSocketRateLimitMiddleware,
            limit_per_minute=self._settings.websocket_rate_limit_requests,
            by_jwt=self._settings.RATE_LIMIT_BY_JWT,
            jwt_secret=self._settings.JWT_SECRET,
            jwt_algorithm=self._settings.JWT_ALGORITHM,
        )
        app.add_middleware(
            RateLimitMiddleware,
            limit_per_minute=self._settings.rate_limit_requests,
            public_limit_per_minute=self._settings.public_rate_limit_requests,
            sensitive_limit_per_minute=self._settings.sensitive_rate_limit_requests,
            by_jwt=self._settings.RATE_LIMIT_BY_JWT,
            jwt_secret=self._settings.JWT_SECRET,
            jwt_algorithm=self._settings.JWT_ALGORITHM,
        )
        app.add_middleware(
            JsonAccessLogMiddleware,
            stats_ttl_seconds=self._settings.STATS_TTL_SECONDS,
            jwt_secret=self._settings.JWT_SECRET,
            jwt_algorithm=self._settings.JWT_ALGORITHM,
        )
        app.add_middleware(RequestContextMiddleware)
        app.add_middleware(
            GatewaySecurityMiddleware,
            max_body_size_bytes=self._settings.max_body_size_bytes,
            security_headers=self._build_security_headers(),
        )
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self._settings.CORS_ORIGINS,
            allow_credentials=self._settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=self._settings.CORS_METHODS,
            allow_headers=self._settings.CORS_HEADERS,
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        logger = structlog.get_logger("api_gateway")
        logger.info("Starting API Gateway", version=self._settings.APP_VERSION)
        app.state.swagger_page.load()
        if app.state.redis is None:
            app.state.redis = redis.from_url(self._settings.REDIS_URL)
            app.state.owns_redis = True
        if app.state.http_client is None:
            timeout = httpx.Timeout(self._settings.SERVICE_TIMEOUT_SECONDS)
            app.state.http_client = httpx.AsyncClient(timeout=timeout)
            app.state.owns_http_client = True
        self._configure_gateway_services(app)

        yield

        logger.info("Shutting down API Gateway")
        if app.state.owns_http_client:
            await app.state.http_client.aclose()
        if app.state.owns_redis:
            await app.state.redis.aclose()
        shutdown_logging()

    def _configure_gateway_services(self, app: FastAPI) -> None:
        cache = GatewayCache(app.state.redis, self._settings.CACHE_TTL_SECONDS)
        service_registry = ServiceRegistry(self._settings)
        header_policy = HeaderPolicy()
        app.state.cache = cache
        app.state.service_registry = service_registry
        if app.state.http_client is None:
            app.state.proxy = None
            app.state.openapi_aggregator = None
            return
        app.state.openapi_aggregator = OpenAPIAggregator(
            http_client=app.state.http_client,
            service_registry=service_registry,
        )
        app.state.proxy = UpstreamProxy(
            settings=self._settings,
            http_client=app.state.http_client,
            cache=cache,
            service_registry=service_registry,
            header_policy=header_policy,
        )

    def _build_security_headers(self) -> dict[str, str]:
        hsts_value = f"max-age={self._settings.HSTS_MAX_AGE_SECONDS}"
        if self._settings.HSTS_INCLUDE_SUBDOMAINS:
            hsts_value += "; includeSubDomains"
        if self._settings.HSTS_PRELOAD:
            hsts_value += "; preload"
        return {
            "Strict-Transport-Security": hsts_value,
            "Content-Security-Policy": self._settings.CONTENT_SECURITY_POLICY,
            "X-Frame-Options": self._settings.X_FRAME_OPTIONS,
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": self._settings.REFERRER_POLICY,
            "Permissions-Policy": self._settings.PERMISSIONS_POLICY,
        }


def create_app(
    settings: GatewaySettings | None = None,
    *,
    redis_client: redis.Redis | None = None,
    http_client: httpx.AsyncClient | None = None,
) -> FastAPI:
    return GatewayApplicationFactory(
        settings or get_settings(),
        redis_client=redis_client,
        http_client=http_client,
    ).create()


app = create_app()
