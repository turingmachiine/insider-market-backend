from src.auth_service.infrastructure.db.tables.permissions_table import (
    permissions_table,
)
from src.auth_service.infrastructure.db.tables.role_permissions_table import (
    role_permissions_table,
)
from src.auth_service.infrastructure.db.tables.roles_table import roles_table
from src.auth_service.infrastructure.db.tables.user_roles_table import user_roles_table
from src.auth_service.infrastructure.db.tables.users_table import users_table

__all__ = [
    "permissions_table",
    "role_permissions_table",
    "roles_table",
    "user_roles_table",
    "users_table",
]
