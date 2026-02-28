"""Интерфейс маппера DTO в Response схему"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

DTO = TypeVar("DTO")
Response = TypeVar("Response", covariant=True)


class ResponseMapper(ABC, Generic[DTO, Response]):
    """Базовый интерфейс маппера DTO в Response схему"""

    @abstractmethod
    def to_response(self, dto: DTO) -> Response:
        """Конвертировать DTO в Response схему"""
        pass
