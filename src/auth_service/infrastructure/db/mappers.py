from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import relationship

from src.auth_service.domain.entities import Permission, Role, User
from src.auth_service.infrastructure.db.metadata import mapper_registry
from src.auth_service.infrastructure.db.tables import (
    permissions_table,
    role_permissions_table,
    roles_table,
    user_roles_table,
    users_table,
)


def setup_mapping() -> None:
    """
    Настроить императивный маппинг SQLAlchemy для auth моделей.
    Должна вызываться при старте приложения.
    """
    try:
        inspect(User)
        return
    except NoInspectionAvailable:
        pass

    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "roles": relationship(
                Role,
                secondary=user_roles_table,
                back_populates="users",
                lazy="selectin",
            )
        },
    )
    mapper_registry.map_imperatively(
        Role,
        roles_table,
        properties={
            "users": relationship(
                User,
                secondary=user_roles_table,
                back_populates="roles",
                lazy="selectin",
            ),
            "permissions": relationship(
                Permission,
                secondary=role_permissions_table,
                back_populates="roles",
                lazy="selectin",
            ),
        },
    )
    mapper_registry.map_imperatively(
        Permission,
        permissions_table,
        properties={
            "roles": relationship(
                Role,
                secondary=role_permissions_table,
                back_populates="permissions",
                lazy="selectin",
            )
        },
    )


__all__ = ["setup_mapping"]
