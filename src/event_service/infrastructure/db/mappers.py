from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.event_service.domain.entities import Event
from src.event_service.infrastructure.db.metadata import mapper_registry
from src.event_service.infrastructure.db.tables import events_table


def setup_mapping() -> None:
    try:
        inspect(Event)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(Event, events_table)


__all__ = ["setup_mapping"]
