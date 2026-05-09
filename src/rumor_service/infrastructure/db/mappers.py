from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.rumor_service.domain.entities import RawPublication, Rumor, Source
from src.rumor_service.infrastructure.db.metadata import mapper_registry
from src.rumor_service.infrastructure.db.tables import (
    raw_publications_table,
    rumors_table,
    sources_table,
)


def setup_mapping() -> None:
    try:
        inspect(Source)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(Source, sources_table)
    mapper_registry.map_imperatively(RawPublication, raw_publications_table)
    mapper_registry.map_imperatively(Rumor, rumors_table)


__all__ = ["setup_mapping"]
