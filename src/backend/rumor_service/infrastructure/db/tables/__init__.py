from src.backend.rumor_service.infrastructure.db.tables.raw_publications_table import (
    raw_publications_table,
)
from src.backend.rumor_service.infrastructure.db.tables.rumors_table import rumors_table
from src.backend.rumor_service.infrastructure.db.tables.sources_table import (
    sources_table,
)

__all__ = ["raw_publications_table", "rumors_table", "sources_table"]
