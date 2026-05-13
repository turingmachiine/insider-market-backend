"""seed access control reference data

Revision ID: 005_seed_access_control
Revises: 004_password_security
Create Date: 2026-05-13
"""

from typing import Sequence
from uuid import UUID, uuid5

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert

revision: str = "005_seed_access_control"
down_revision: str | None = "004_password_security"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SEED_NAMESPACE = UUID("5d9ffb0b-9d58-4d78-9e2e-961a3713e94f")


# Константы повторяющихся прав
PERM_AUTH_PERMISSIONS_READ = "auth:permissions:read"
PERM_AUTH_USERS_READ = "auth:users:read"
PERM_AUTH_USERS_WRITE = "auth:users:write"
PERM_AUTH_ROLES_WRITE = "auth:roles:write"

PERM_ADMIN_READ = "admin:read"
PERM_ADMIN_WRITE = "admin:write"

PERM_NSI_READ = "nsi:read"
PERM_NSI_WRITE = "nsi:write"

PERM_PROFILE_READ = "profile:read"
PERM_PROFILE_READ_ANY = "profile:read:any"
PERM_PROFILE_WRITE = "profile:write"

PERM_RATING_READ = "rating:read"
PERM_RATING_READ_ANY = "rating:read:any"
PERM_RATING_WRITE = "rating:write"
PERM_RATING_JOBS_RUN = "rating:jobs:run"

PERM_EVENT_READ = "event:read"
PERM_EVENT_WRITE = "event:write"
PERM_EVENT_MODERATE = "event:moderate"
PERM_EVENT_JOBS_RUN = "event:jobs:run"

PERM_MARKET_READ = "market:read"
PERM_MARKET_WRITE = "market:write"
PERM_MARKET_TRADE = "market:trade"
PERM_MARKET_MANAGE = "market:manage"

PERM_RUMOR_READ = "rumor:read"
PERM_RUMOR_WRITE = "rumor:write"
PERM_RUMOR_MODERATE = "rumor:moderate"

PERM_NOTIFICATION_READ = "notification:read"
PERM_NOTIFICATION_READ_ANY = "notification:read:any"
PERM_NOTIFICATION_PUBLISH = "notification:publish"

PERM_TEAM_WRITE = "team:write"
PERM_TEAM_READ_ANY = "team:read:any"

PERM_WALLET_READ_ANY = "wallet:read:any"

ROLE_PERMISSIONS = {
    "user": {
        PERM_AUTH_PERMISSIONS_READ,
        PERM_NSI_READ,
        PERM_PROFILE_READ,
        PERM_PROFILE_WRITE,
        PERM_RATING_READ,
        PERM_EVENT_READ,
        PERM_MARKET_READ,
        PERM_MARKET_TRADE,
        PERM_RUMOR_READ,
        PERM_NOTIFICATION_READ,
        PERM_TEAM_WRITE,
    },
    "analyst": {
        PERM_AUTH_PERMISSIONS_READ,
        PERM_NSI_READ,
        PERM_NSI_WRITE,
        PERM_PROFILE_READ,
        PERM_PROFILE_WRITE,
        PERM_RATING_READ,
        PERM_RATING_READ_ANY,
        PERM_RATING_WRITE,
        PERM_EVENT_READ,
        PERM_EVENT_WRITE,
        PERM_MARKET_READ,
        PERM_MARKET_WRITE,
        PERM_RUMOR_READ,
        PERM_RUMOR_WRITE,
        PERM_TEAM_WRITE,
    },
    "moderator": {
        PERM_AUTH_PERMISSIONS_READ,
        PERM_ADMIN_READ,
        PERM_NSI_READ,
        PERM_PROFILE_READ,
        PERM_EVENT_READ,
        PERM_EVENT_MODERATE,
        PERM_MARKET_READ,
        PERM_RUMOR_READ,
        PERM_RUMOR_MODERATE,
        PERM_NOTIFICATION_READ,
        PERM_NOTIFICATION_PUBLISH,
        PERM_TEAM_WRITE,
    },
    "admin": {
        PERM_AUTH_PERMISSIONS_READ,
        PERM_AUTH_USERS_READ,
        PERM_AUTH_USERS_WRITE,
        PERM_AUTH_ROLES_WRITE,
        PERM_ADMIN_READ,
        PERM_ADMIN_WRITE,
        PERM_EVENT_JOBS_RUN,
        PERM_EVENT_MODERATE,
        PERM_EVENT_READ,
        PERM_EVENT_WRITE,
        PERM_MARKET_MANAGE,
        PERM_MARKET_READ,
        PERM_MARKET_TRADE,
        PERM_MARKET_WRITE,
        PERM_NOTIFICATION_PUBLISH,
        PERM_NOTIFICATION_READ,
        PERM_NOTIFICATION_READ_ANY,
        PERM_NSI_READ,
        PERM_NSI_WRITE,
        PERM_PROFILE_READ,
        PERM_PROFILE_READ_ANY,
        PERM_PROFILE_WRITE,
        PERM_RATING_JOBS_RUN,
        PERM_RATING_READ,
        PERM_RATING_READ_ANY,
        PERM_RATING_WRITE,
        PERM_RUMOR_MODERATE,
        PERM_RUMOR_READ,
        PERM_RUMOR_WRITE,
        PERM_TEAM_READ_ANY,
        PERM_TEAM_WRITE,
        PERM_WALLET_READ_ANY,
    },
    "system": {
        PERM_AUTH_PERMISSIONS_READ,
        PERM_AUTH_USERS_WRITE,
        PERM_AUTH_ROLES_WRITE,
        PERM_ADMIN_READ,
        PERM_ADMIN_WRITE,
        PERM_NSI_READ,
        PERM_NSI_WRITE,
        PERM_TEAM_READ_ANY,
        PERM_EVENT_READ,
        PERM_EVENT_WRITE,
        PERM_EVENT_MODERATE,
        PERM_EVENT_JOBS_RUN,
        PERM_MARKET_READ,
        PERM_MARKET_WRITE,
        PERM_MARKET_MANAGE,
        PERM_WALLET_READ_ANY,
        PERM_NOTIFICATION_PUBLISH,
        PERM_NOTIFICATION_READ_ANY,
        PERM_PROFILE_READ,
        PERM_PROFILE_READ_ANY,
        PERM_PROFILE_WRITE,
        PERM_RATING_READ,
        PERM_RATING_WRITE,
        PERM_RATING_JOBS_RUN,
        PERM_RUMOR_READ,
        PERM_RUMOR_WRITE,
        PERM_RUMOR_MODERATE,
        PERM_TEAM_WRITE,
    },
}

roles_table = sa.table(
    "roles",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("name", sa.String),
)
permissions_table = sa.table(
    "permissions",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("name", sa.String),
)
role_permissions_table = sa.table(
    "role_permissions",
    sa.column("role_id", postgresql.UUID(as_uuid=True)),
    sa.column("permission_id", postgresql.UUID(as_uuid=True)),
)


def _id(kind: str, name: str) -> UUID:
    return uuid5(SEED_NAMESPACE, f"{kind}:{name}")


def upgrade() -> None:
    bind = op.get_bind()
    permissions = sorted(
        {permission for values in ROLE_PERMISSIONS.values() for permission in values}
    )
    bind.execute(
        insert(permissions_table)
        .values(
            [
                {"id": _id("permission", permission), "name": permission}
                for permission in permissions
            ]
        )
        .on_conflict_do_nothing(index_elements=["name"])
    )
    bind.execute(
        insert(roles_table)
        .values(
            [
                {"id": _id("role", role), "name": role}
                for role in sorted(ROLE_PERMISSIONS)
            ]
        )
        .on_conflict_do_nothing(index_elements=["name"])
    )

    # Исправление: преобразуем результат в словарь вручную
    role_rows = {
        row.name: row.id
        for row in bind.execute(
            sa.select(roles_table.c.name, roles_table.c.id).where(
                roles_table.c.name.in_(ROLE_PERMISSIONS)
            )
        )
    }

    permission_rows = {
        row.name: row.id
        for row in bind.execute(
            sa.select(permissions_table.c.name, permissions_table.c.id).where(
                permissions_table.c.name.in_(permissions)
            )
        )
    }

    bind.execute(
        insert(role_permissions_table)
        .values(
            [
                {
                    "role_id": role_rows[role],
                    "permission_id": permission_rows[permission],
                }
                for role, role_permissions in sorted(ROLE_PERMISSIONS.items())
                for permission in sorted(role_permissions)
            ]
        )
        .on_conflict_do_nothing(index_elements=["role_id", "permission_id"])
    )


def downgrade() -> None:
    permissions = sorted(
        {permission for values in ROLE_PERMISSIONS.values() for permission in values}
    )
    op.execute(
        role_permissions_table.delete().where(
            role_permissions_table.c.role_id.in_(
                [_id("role", role) for role in ROLE_PERMISSIONS]
            )
        )
    )
    op.execute(roles_table.delete().where(roles_table.c.name.in_(ROLE_PERMISSIONS)))
    op.execute(
        permissions_table.delete().where(permissions_table.c.name.in_(permissions))
    )
