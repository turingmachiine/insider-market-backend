"""Protocol для мапперов обновления"""

from typing import Protocol


class UpdateMapper[DTO, Entity](Protocol):
    """Protocol для мапперов обновления"""

    def apply_to_entity(self, dto: DTO, entity: Entity) -> Entity:
        """Применить DTO к сущности"""
        ...
