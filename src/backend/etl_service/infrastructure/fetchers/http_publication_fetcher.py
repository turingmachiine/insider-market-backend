from datetime import datetime
from hashlib import sha256
from html.parser import HTMLParser
from typing import Any

import httpx

from src.backend.etl_service.application.dto import SourceDTO
from src.backend.etl_service.domain.entities import ExternalPublication


class TelegramPostParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._inside_message = False
        self._current_parts: list[str] = []
        self.posts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class") or ""
        if tag == "div" and "tgme_widget_message_text" in class_name:
            self._inside_message = True
            self._current_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._inside_message:
            text = " ".join(part.strip() for part in self._current_parts).strip()
            if text:
                self.posts.append(text)
            self._inside_message = False

    def handle_data(self, data: str) -> None:
        if self._inside_message:
            self._current_parts.append(data)


class HttpPublicationFetcher:
    def __init__(self, http_client: httpx.AsyncClient, *, limit: int = 20) -> None:
        self._http_client = http_client
        self._limit = limit

    async def fetch(self, source: SourceDTO) -> list[ExternalPublication]:
        source_url = self._build_source_url(source)
        if source_url is None:
            return []

        response = await self._http_client.get(source_url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return self._parse_json(response.json())[: self._limit]
        if source.source_type == "telegram":
            return self._parse_telegram_html(response.text, source)[: self._limit]
        return [
            ExternalPublication(
                text=response.text.strip(),
                external_id=source_url,
                url=source_url,
                payload={"source_format": "text"},
            )
        ][: self._limit]

    @staticmethod
    def _build_source_url(source: SourceDTO) -> str | None:
        if source.url:
            return source.url
        if source.source_type == "telegram" and source.handle:
            handle = source.handle.lstrip("@")
            return f"https://t.me/s/{handle}"
        return None

    def _parse_json(self, payload: Any) -> list[ExternalPublication]:
        items = payload if isinstance(payload, list) else payload.get("items", [])
        if not isinstance(items, list):
            return []

        publications = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("content") or item.get("message")
            if not text:
                continue
            publications.append(
                ExternalPublication(
                    text=str(text),
                    external_id=self._optional_str(item.get("id")),
                    url=self._optional_str(item.get("url")),
                    published_at=self._parse_optional_datetime(
                        self._optional_str(item.get("published_at"))
                    ),
                    payload={"source_format": "json", "raw": item},
                )
            )
        return publications

    @staticmethod
    def _parse_telegram_html(
        html: str,
        source: SourceDTO,
    ) -> list[ExternalPublication]:
        parser = TelegramPostParser()
        parser.feed(html)
        handle = (source.handle or source.name).lstrip("@")
        publications = []
        for index, text in enumerate(parser.posts):
            text_hash = sha256(text.encode("utf-8")).hexdigest()[:16]
            publications.append(
                ExternalPublication(
                    text=text,
                    external_id=f"telegram:{handle}:{index}:{text_hash}",
                    url=f"https://t.me/s/{handle}",
                    payload={"source_format": "telegram_html"},
                )
            )
        return publications

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _parse_optional_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)
