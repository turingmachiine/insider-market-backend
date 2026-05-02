import asyncio

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from src.backend.api_gateway.config import GatewaySettings
from src.backend.api_gateway.services.cache import GatewayCache
from src.backend.api_gateway.services.headers import HeaderPolicy
from src.backend.api_gateway.services.service_registry import (
    ServiceName,
    ServiceRegistry,
    UpstreamService,
)


class UpstreamProxy:
    def __init__(
        self,
        settings: GatewaySettings,
        http_client: httpx.AsyncClient,
        cache: GatewayCache,
        service_registry: ServiceRegistry,
        header_policy: HeaderPolicy,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._cache = cache
        self._service_registry = service_registry
        self._header_policy = header_policy

    async def forward(
        self,
        request: Request,
        service_name: ServiceName,
        target_path: str,
    ) -> Response:
        service = self._service_registry.get(service_name)
        cached_response = await self._get_cached_response(request, service)
        if cached_response is not None:
            return cached_response

        await self._invalidate_cache_if_needed(request, service)
        upstream_response = await self._call_upstream(request, service, target_path)
        if isinstance(upstream_response, Response):
            return upstream_response

        return await self._build_response(request, service, upstream_response)

    async def _get_cached_response(
        self,
        request: Request,
        service: UpstreamService,
    ) -> Response | None:
        if not self._should_cache(request, service):
            return None

        cached = await self._cache.get(request.url.path, request.scope["query_string"])
        if cached is None:
            return None
        return Response(
            content=cached["body"],
            status_code=cached["status_code"],
            headers=cached["headers"],
        )

    async def _invalidate_cache_if_needed(
        self,
        request: Request,
        service: UpstreamService,
    ) -> None:
        if service.invalidate_on_mutation and request.method in {"PUT", "DELETE"}:
            await self._cache.invalidate_path(request.url.path)

    async def _call_upstream(
        self,
        request: Request,
        service: UpstreamService,
        target_path: str,
    ) -> httpx.Response | Response:
        target_url = service.build_url(target_path, request.url.query)
        try:
            async with asyncio.timeout(self._settings.TOTAL_TIMEOUT_SECONDS):
                return await self._http_client.request(
                    request.method,
                    target_url,
                    content=await request.body(),
                    headers=self._header_policy.build_upstream_headers(request),
                    timeout=self._settings.SERVICE_TIMEOUT_SECONDS,
                )
        except TimeoutError:
            return JSONResponse({"detail": "Upstream timeout"}, status_code=504)
        except httpx.HTTPError:
            return JSONResponse(
                {"detail": "Upstream service unavailable"},
                status_code=502,
            )

    async def _build_response(
        self,
        request: Request,
        service: UpstreamService,
        upstream_response: httpx.Response,
    ) -> Response:
        headers = self._header_policy.build_downstream_headers(
            upstream_response.headers
        )
        response = Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=headers,
            media_type=upstream_response.headers.get("content-type"),
        )
        if self._should_cache(request, service):
            await self._cache.set(
                request.url.path,
                request.scope["query_string"],
                upstream_response.status_code,
                headers,
                upstream_response.content,
            )
        return response

    @staticmethod
    def _should_cache(request: Request, service: UpstreamService) -> bool:
        return service.cache_get and request.method == "GET"
