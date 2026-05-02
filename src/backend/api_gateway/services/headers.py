from collections.abc import Mapping

from fastapi import Request


class HeaderPolicy:
    _HOP_BY_HOP_HEADERS = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
    _REQUEST_BLOCKED_HEADERS = _HOP_BY_HOP_HEADERS | {"host", "content-length"}
    _RESPONSE_BLOCKED_HEADERS = _HOP_BY_HOP_HEADERS | {
        "content-length",
        "content-encoding",
    }

    def build_upstream_headers(self, request: Request) -> dict[str, str]:
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in self._REQUEST_BLOCKED_HEADERS
            and key.lower() != "x-forwarded-for"
        }
        if request.client:
            headers["x-forwarded-for"] = request.client.host
        return headers

    def build_downstream_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        return {
            key: value
            for key, value in headers.items()
            if key.lower() not in self._RESPONSE_BLOCKED_HEADERS
        }
