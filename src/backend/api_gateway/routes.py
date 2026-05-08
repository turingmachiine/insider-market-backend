import httpx
from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from src.backend.api_gateway.presentation.swagger_page import SwaggerLandingPage
from src.backend.api_gateway.services.openapi import OpenAPIAggregator
from src.backend.api_gateway.services.proxy import UpstreamProxy
from src.backend.api_gateway.services.service_registry import ServiceName


class GatewayRouter:
    def __init__(self) -> None:
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            tags=["Health"],
        )
        self.router.add_api_route(
            "/swagger/",
            self.swagger_redirect,
            methods=["GET"],
            include_in_schema=False,
        )
        self.router.add_api_route(
            "/docs",
            self.swagger_index,
            methods=["GET"],
            include_in_schema=False,
        )
        self.router.add_api_route(
            "/swagger-ui",
            self.swagger_ui,
            methods=["GET"],
            include_in_schema=False,
        )
        self.router.add_api_route(
            "/swagger/swagger.json",
            self.aggregate_swagger_json,
            methods=["GET"],
            include_in_schema=False,
        )
        self.router.add_api_route(
            "/swagger/{service}/swagger.json",
            self.swagger_json,
            methods=["GET"],
            include_in_schema=False,
        )
        self._register_proxy_routes(
            service=ServiceName.NSI,
            prefix=f"/{ServiceName.NSI}",
        )
        self._register_proxy_routes(
            service=ServiceName.AUTH,
            prefix=f"/{ServiceName.AUTH}",
        )
        self._register_proxy_routes(
            service=ServiceName.RUMOR,
            prefix=f"/{ServiceName.RUMOR}",
        )
        self._register_proxy_routes(
            service=ServiceName.EVENT,
            prefix=f"/{ServiceName.EVENT}",
        )
        self._register_proxy_routes(
            service=ServiceName.MARKET,
            prefix=f"/{ServiceName.MARKET}",
        )
        self._register_proxy_routes(
            service=ServiceName.NOTIFICATION,
            prefix=f"/{ServiceName.NOTIFICATION}",
        )
        self._register_proxy_routes(
            service=ServiceName.PROFILE,
            prefix=f"/{ServiceName.PROFILE}",
        )
        self._register_proxy_routes(
            service=ServiceName.RATING,
            prefix=f"/{ServiceName.RATING}",
        )

    def _register_proxy_routes(self, service: ServiceName, prefix: str) -> None:
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

        async def proxy_root(request: Request) -> Response:
            return await self._proxy(request, service, "")

        async def proxy_path(request: Request, target_path: str) -> Response:
            return await self._proxy(request, service, target_path)

        self.router.add_api_route(prefix, proxy_root, methods=methods)
        self.router.add_api_route(
            f"{prefix}/{{target_path:path}}",
            proxy_path,
            methods=methods,
        )

    @staticmethod
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    @staticmethod
    def swagger_redirect() -> RedirectResponse:
        return RedirectResponse(url="/docs", status_code=308)

    @staticmethod
    def swagger_index(request: Request) -> HTMLResponse:
        swagger_page: SwaggerLandingPage = request.app.state.swagger_page
        return HTMLResponse(swagger_page.render())

    @staticmethod
    def swagger_ui(url: str = "/swagger/swagger.json") -> HTMLResponse:
        return get_swagger_ui_html(openapi_url=url, title="Football Research Gateway")

    @staticmethod
    async def aggregate_swagger_json(request: Request) -> JSONResponse:
        aggregator: OpenAPIAggregator | None = request.app.state.openapi_aggregator
        if aggregator is None:
            return JSONResponse(
                {"detail": "OpenAPI aggregator is not configured"},
                status_code=503,
            )
        try:
            return JSONResponse(await aggregator.aggregate())
        except httpx.HTTPError:
            return JSONResponse(
                {"detail": "Failed to load upstream OpenAPI schema"},
                status_code=502,
            )

    async def swagger_json(self, request: Request, service: str) -> Response:
        try:
            service_name = ServiceName(service)
        except ValueError:
            return JSONResponse({"detail": "Unknown service"}, status_code=404)
        return await self._proxy(request, service_name, "openapi.json")

    @staticmethod
    async def _proxy(
        request: Request,
        service: ServiceName,
        target_path: str,
    ) -> Response:
        proxy: UpstreamProxy = request.app.state.proxy
        return await proxy.forward(request, service, target_path)


router = GatewayRouter().router
