"""Базовый интерфейс маппера между сущностью и DTO"""

from abc import ABC, abstractmethod


class Mapper[Entity, DTO](ABC):
    """Базовый интерфейс маппера между сущностью и DTO"""

    @abstractmethod
    def to_dto(self, entity: Entity) -> DTO:
        """Конвертировать сущность в DTO"""
        pass

    @abstractmethod
    def to_entity(self, dto: DTO) -> Entity:
        """Конвертировать DTO в сущность"""
        pass
