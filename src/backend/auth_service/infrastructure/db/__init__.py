from src.backend.auth_service.domain.entities import Permission, Role, User
from src.backend.auth_service.infrastructure.db.database import (
    create_engine,
    create_session_factory,
)
from src.backend.auth_service.infrastructure.db.mappers import setup_mapping
from src.backend.auth_service.infrastructure.db.metadata import Base
from src.backend.auth_service.infrastructure.db.tables import (
    role_permissions_table,
    user_roles_table,
)

user_roles = user_roles_table
role_permissions = role_permissions_table

__all__ = [
    "Base",
    "Permission",
    "Role",
    "User",
    "create_engine",
    "create_session_factory",
    "role_permissions",
    "setup_mapping",
    "user_roles",
]
