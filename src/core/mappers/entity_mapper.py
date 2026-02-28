"""Protocol для мапперов сущностей"""

from typing import Protocol


class EntityMapper[Entity, DTO](Protocol):
    """Protocol для мапперов сущностей"""

    def to_dto(self, entity: Entity) -> DTO:
        """Конвертировать сущность в DTO"""
        ...

    def to_entity(self, dto: DTO) -> Entity:
        """Конвертировать DTO в сущность"""
        ...
