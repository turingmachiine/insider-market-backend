"""Базовые интерфейсы маппинга между слоями"""

from src.nsi_service.core.mappers.create_mapper import CreateMapper
from src.nsi_service.core.mappers.entity_mapper import EntityMapper
from src.nsi_service.core.mappers.mapper import Mapper
from src.nsi_service.core.mappers.response_mapper import ResponseMapper
from src.nsi_service.core.mappers.update_mapper import UpdateMapper

__all__ = [
    "Mapper",
    "EntityMapper",
    "CreateMapper",
    "UpdateMapper",
    "ResponseMapper",
]
