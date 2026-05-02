# src/presentation/api/v1/mappers/base_response_mapper.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from typing_extensions import Protocol, runtime_checkable

# Используем ковариантность для возвращаемых типов и контравариантность для параметров
T_contra = TypeVar("T_contra", contravariant=True)  # для DTO (входной параметр)
R_co = TypeVar("R_co", covariant=True)  # для Response (возвращаемое значение)


@runtime_checkable
class IBaseResponseMapper(Protocol[T_contra, R_co]):
    """Протокол маппера ответов (без наследования от ABC)"""

    def to_response(self, dto: T_contra) -> R_co:
        """Преобразовать DTO в Response"""
        ...


# Или если нужен ABC:
class BaseResponseMapper(Generic[T_contra, R_co], ABC):
    """Абстрактный базовый класс маппера ответов"""

    @abstractmethod
    def to_response(self, dto: T_contra) -> R_co:
        """Преобразовать DTO в Response"""
        pass
