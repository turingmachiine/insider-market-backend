from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from src.backend.etl_service.application.dto import (
    CreateRawPublicationDTO,
    CreateRumorDTO,
    RawPublicationDTO,
    RumorDTO,
    SourceDTO,
)


class RumorServiceHttpClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def get_active_sources(self) -> list[SourceDTO]:
        response = await self._http_client.get(
            "/api/v1/sources",
            params={"active_only": "true", "limit": 500},
        )
        response.raise_for_status()
        return [
            self._source_from_payload(item) for item in response.json().get("items", [])
        ]

    async def get_raw_publications_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RawPublicationDTO]:
        response = await self._http_client.get(
            f"/api/v1/raw-publications/source/{source_id}",
            params={"limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return [
            self._raw_publication_from_payload(item)
            for item in response.json().get("items", [])
        ]

    async def create_raw_publication(
        self,
        dto: CreateRawPublicationDTO,
    ) -> RawPublicationDTO:
        response = await self._http_client.post(
            "/api/v1/raw-publications",
            json=self._create_raw_publication_payload(dto),
        )
        response.raise_for_status()
        return self._raw_publication_from_payload(response.json())

    async def get_rumors_by_source(
        self,
        source_id: UUID,
        *,
        limit: int,
        offset: int = 0,
    ) -> list[RumorDTO]:
        response = await self._http_client.get(
            "/api/v1/rumors",
            params={"source_id": str(source_id), "limit": limit, "offset": offset},
        )
        response.raise_for_status()
        return [
            self._rumor_from_payload(item) for item in response.json().get("items", [])
        ]

    async def create_rumor(self, dto: CreateRumorDTO) -> RumorDTO:
        response = await self._http_client.post(
            "/api/v1/rumors",
            json=self._create_rumor_payload(dto),
        )
        response.raise_for_status()
        return self._rumor_from_payload(response.json())

    @staticmethod
    def _source_from_payload(payload: dict[str, Any]) -> SourceDTO:
        return SourceDTO(
            id=UUID(payload["id"]),
            name=payload["name"],
            source_type=payload["source_type"],
            handle=payload.get("handle"),
            url=payload.get("url"),
            weight=float(payload["weight"]),
            is_active=bool(payload["is_active"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )

    @staticmethod
    def _raw_publication_from_payload(payload: dict[str, Any]) -> RawPublicationDTO:
        return RawPublicationDTO(
            id=UUID(payload["id"]),
            source_id=UUID(payload["source_id"]),
            text=payload["text"],
            external_id=payload.get("external_id"),
            url=payload.get("url"),
            published_at=RumorServiceHttpClient._parse_optional_datetime(
                payload.get("published_at")
            ),
            collected_at=datetime.fromisoformat(payload["collected_at"]),
            payload=payload.get("payload", {}),
        )

    @staticmethod
    def _rumor_from_payload(payload: dict[str, Any]) -> RumorDTO:
        raw_publication_id = payload.get("raw_publication_id")
        return RumorDTO(
            id=UUID(payload["id"]),
            source_id=UUID(payload["source_id"]),
            title=payload["title"],
            text=payload["text"],
            normalized_text=payload.get("normalized_text"),
            raw_publication_id=(
                UUID(raw_publication_id) if raw_publication_id else None
            ),
            confidence_score=float(payload["confidence_score"]),
            status=payload["status"],
            tags=payload.get("tags", []),
            event_candidate_payload=payload.get("event_candidate_payload", {}),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )

    @staticmethod
    def _create_raw_publication_payload(
        dto: CreateRawPublicationDTO,
    ) -> dict[str, Any]:
        return {
            "source_id": str(dto.source_id),
            "text": dto.text,
            "external_id": dto.external_id,
            "url": dto.url,
            "published_at": (
                dto.published_at.isoformat() if dto.published_at else None
            ),
            "payload": dto.payload,
        }

    @staticmethod
    def _create_rumor_payload(dto: CreateRumorDTO) -> dict[str, Any]:
        return {
            "source_id": str(dto.source_id),
            "title": dto.title,
            "text": dto.text,
            "normalized_text": dto.normalized_text,
            "raw_publication_id": str(dto.raw_publication_id),
            "confidence_score": dto.confidence_score,
            "status": dto.status,
            "tags": dto.tags,
            "event_candidate_payload": dto.event_candidate_payload,
        }

    @staticmethod
    def _parse_optional_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)
