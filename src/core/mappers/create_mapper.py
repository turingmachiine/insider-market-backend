"""Protocol для мапперов создания"""

from typing import Protocol


class CreateMapper[DTO, Entity](Protocol):
    """Protocol для мапперов создания"""

    def create_entity(self, dto: DTO) -> Entity:
        """Создать сущность из DTO"""
        ...
