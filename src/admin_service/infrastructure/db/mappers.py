from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from src.admin_service.domain.entities import AdminAction, SavedFilter
from src.admin_service.infrastructure.db.metadata import mapper_registry
from src.admin_service.infrastructure.db.tables import (
    admin_actions_table,
    saved_filters_table,
)


def setup_mapping() -> None:
    try:
        inspect(AdminAction)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(AdminAction, admin_actions_table)
    mapper_registry.map_imperatively(SavedFilter, saved_filters_table)


__all__ = ["setup_mapping"]
