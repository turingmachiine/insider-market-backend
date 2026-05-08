from copy import deepcopy
from typing import Any, cast

import httpx

from src.backend.api_gateway.services.service_registry import (
    ServiceName,
    ServiceRegistry,
)


class OpenAPIAggregator:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        service_registry: ServiceRegistry,
    ) -> None:
        self._http_client = http_client
        self._service_registry = service_registry

    async def aggregate(self) -> dict[str, Any]:
        documents = {}
        for service_name in ServiceName:
            documents[service_name] = await self._fetch_service_schema(service_name)

        components: dict[str, dict[str, Any]] = {}
        paths: dict[str, Any] = {}
        tags: dict[str, dict[str, str]] = {}

        for service_name, document in documents.items():
            component_name_map = self._build_component_name_map(
                service_name,
                document,
            )
            rewritten = self._rewrite_refs(deepcopy(document), component_name_map)
            self._merge_components(
                components,
                self._prefix_components(service_name, rewritten.get("components", {})),
            )
            paths.update(self._prefix_paths(service_name, rewritten.get("paths", {})))
            self._merge_tags(tags, rewritten.get("tags", []))

        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Football Research API",
                "version": "0.1.0",
                "description": (
                    "Единая OpenAPI-схема gateway для реализованных сервисов "
                    "Football Research: NSI, Auth, Rumor, Event, Market, "
                    "Notification, Profile и Rating."
                ),
            },
            "servers": [{"url": "/"}],
            "tags": list(tags.values()),
            "paths": paths,
            "components": components,
        }

    async def _fetch_service_schema(self, service_name: ServiceName) -> dict[str, Any]:
        service = self._service_registry.get(service_name)
        response = await self._http_client.get(service.build_url("openapi.json"))
        response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def _build_component_name_map(
        self,
        service_name: ServiceName,
        document: dict[str, Any],
    ) -> dict[str, str]:
        component_name_map = {}
        prefix = self._component_prefix(service_name)
        for section, values in document.get("components", {}).items():
            if section != "securitySchemes" and isinstance(values, dict):
                for name in values:
                    component_name_map[
                        f"#/components/{section}/{name}"
                    ] = f"#/components/{section}/{prefix}{name}"
        return component_name_map

    def _rewrite_refs(
        self,
        value: Any,
        component_name_map: dict[str, str],
    ) -> Any:
        if isinstance(value, dict):
            rewritten = {}
            for key, item in value.items():
                if key == "$ref" and isinstance(item, str):
                    rewritten[key] = component_name_map.get(item, item)
                else:
                    rewritten[key] = self._rewrite_refs(item, component_name_map)
            return rewritten
        if isinstance(value, list):
            return [self._rewrite_refs(item, component_name_map) for item in value]
        return value

    @staticmethod
    def _merge_components(
        target: dict[str, dict[str, Any]],
        source: dict[str, Any],
    ) -> None:
        for section, values in source.items():
            if not isinstance(values, dict):
                continue
            target.setdefault(section, {}).update(values)

    def _prefix_components(
        self,
        service_name: ServiceName,
        components: dict[str, Any],
    ) -> dict[str, Any]:
        prefix = self._component_prefix(service_name)
        prefixed_components = {}
        for section, values in components.items():
            if not isinstance(values, dict):
                continue
            if section == "securitySchemes":
                prefixed_components[section] = values
            else:
                prefixed_components[section] = {
                    f"{prefix}{name}": value for name, value in values.items()
                }
        return prefixed_components

    def _prefix_paths(
        self,
        service_name: ServiceName,
        paths: dict[str, Any],
    ) -> dict[str, Any]:
        prefixed_paths = {}
        for path, path_item in paths.items():
            gateway_path = f"/{service_name.value}{path}"
            prefixed_paths[gateway_path] = self._prefix_operations(
                service_name,
                path_item,
            )
        return prefixed_paths

    def _prefix_operations(self, service_name: ServiceName, path_item: Any) -> Any:
        if not isinstance(path_item, dict):
            return path_item

        rewritten = deepcopy(path_item)
        service_label = self._service_label(service_name)
        for method, operation in rewritten.items():
            if not isinstance(operation, dict):
                continue
            if method.lower() not in {
                "get",
                "put",
                "post",
                "delete",
                "options",
                "head",
                "patch",
                "trace",
            }:
                continue

            operation["tags"] = operation.get("tags", []) or [service_label]
            if "operationId" in operation:
                operation[
                    "operationId"
                ] = f"{service_name.value}_{operation['operationId']}"
        return rewritten

    @staticmethod
    def _merge_tags(
        target: dict[str, dict[str, str]],
        source_tags: list[Any],
    ) -> None:
        if not source_tags:
            return

        for tag in source_tags:
            if not isinstance(tag, dict) or "name" not in tag:
                continue
            target.setdefault(tag["name"], tag)

    @staticmethod
    def _component_prefix(service_name: ServiceName) -> str:
        return "".join(part.title() for part in service_name.value.split("_"))

    @staticmethod
    def _service_label(service_name: ServiceName) -> str:
        return {
            ServiceName.AUTH: "Auth",
            ServiceName.NSI: "NSI",
            ServiceName.RUMOR: "Rumor",
            ServiceName.EVENT: "Event",
            ServiceName.MARKET: "Market",
            ServiceName.NOTIFICATION: "Notification",
            ServiceName.PROFILE: "Profile",
            ServiceName.RATING: "Rating",
        }[service_name]
