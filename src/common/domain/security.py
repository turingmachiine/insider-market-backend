from enum import StrEnum


class Permission(StrEnum):
    AUTH_PERMISSIONS_READ = "auth:permissions:read"
    AUTH_USERS_READ = "auth:users:read"
    AUTH_USERS_WRITE = "auth:users:write"
    AUTH_ROLES_WRITE = "auth:roles:write"

    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"

    EVENT_READ = "event:read"
    EVENT_WRITE = "event:write"
    EVENT_MODERATE = "event:moderate"
    EVENT_JOBS_RUN = "event:jobs:run"

    MARKET_READ = "market:read"
    MARKET_WRITE = "market:write"
    MARKET_TRADE = "market:trade"
    MARKET_MANAGE = "market:manage"
    WALLET_READ_ANY = "wallet:read:any"

    NSI_READ = "nsi:read"
    NSI_WRITE = "nsi:write"
    TEAM_READ_ANY = "team:read:any"
    TEAM_WRITE = "team:write"

    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_READ_ANY = "notification:read:any"
    NOTIFICATION_PUBLISH = "notification:publish"

    PROFILE_READ = "profile:read"
    PROFILE_READ_ANY = "profile:read:any"
    PROFILE_WRITE = "profile:write"

    RATING_READ = "rating:read"
    RATING_READ_ANY = "rating:read:any"
    RATING_WRITE = "rating:write"
    RATING_JOBS_RUN = "rating:jobs:run"

    RUMOR_READ = "rumor:read"
    RUMOR_WRITE = "rumor:write"
    RUMOR_MODERATE = "rumor:moderate"


class Role(StrEnum):
    USER = "user"
    ANALYST = "analyst"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SYSTEM = "system"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.USER: {
        Permission.AUTH_PERMISSIONS_READ,
        Permission.NSI_READ,
        Permission.PROFILE_READ,
        Permission.PROFILE_WRITE,
        Permission.RATING_READ,
        Permission.EVENT_READ,
        Permission.MARKET_READ,
        Permission.MARKET_TRADE,
        Permission.RUMOR_READ,
        Permission.NOTIFICATION_READ,
        Permission.TEAM_WRITE,
    },
    Role.ANALYST: {
        Permission.AUTH_PERMISSIONS_READ,
        Permission.NSI_READ,
        Permission.NSI_WRITE,
        Permission.PROFILE_READ,
        Permission.PROFILE_WRITE,
        Permission.RATING_READ,
        Permission.RATING_READ_ANY,
        Permission.RATING_WRITE,
        Permission.EVENT_READ,
        Permission.EVENT_WRITE,
        Permission.MARKET_READ,
        Permission.MARKET_WRITE,
        Permission.RUMOR_READ,
        Permission.RUMOR_WRITE,
        Permission.TEAM_WRITE,
    },
    Role.MODERATOR: {
        Permission.AUTH_PERMISSIONS_READ,
        Permission.ADMIN_READ,
        Permission.NSI_READ,
        Permission.PROFILE_READ,
        Permission.EVENT_READ,
        Permission.EVENT_MODERATE,
        Permission.MARKET_READ,
        Permission.RUMOR_READ,
        Permission.RUMOR_MODERATE,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_PUBLISH,
        Permission.TEAM_WRITE,
    },
    Role.ADMIN: set(Permission),
    Role.SYSTEM: {
        Permission.AUTH_PERMISSIONS_READ,
        Permission.AUTH_USERS_WRITE,
        Permission.AUTH_ROLES_WRITE,
        Permission.ADMIN_READ,
        Permission.ADMIN_WRITE,
        Permission.NSI_READ,
        Permission.NSI_WRITE,
        Permission.TEAM_READ_ANY,
        Permission.EVENT_READ,
        Permission.EVENT_WRITE,
        Permission.EVENT_MODERATE,
        Permission.EVENT_JOBS_RUN,
        Permission.MARKET_READ,
        Permission.MARKET_WRITE,
        Permission.MARKET_MANAGE,
        Permission.WALLET_READ_ANY,
        Permission.NOTIFICATION_PUBLISH,
        Permission.NOTIFICATION_READ_ANY,
        Permission.PROFILE_READ,
        Permission.PROFILE_READ_ANY,
        Permission.PROFILE_WRITE,
        Permission.RATING_READ,
        Permission.RATING_WRITE,
        Permission.RATING_JOBS_RUN,
        Permission.RUMOR_READ,
        Permission.RUMOR_WRITE,
        Permission.RUMOR_MODERATE,
        Permission.TEAM_WRITE,
    },
}


def normalize_permission(permission: Permission | str) -> str:
    return permission.value if isinstance(permission, Permission) else permission


def normalize_role(role: Role | str) -> str:
    return role.value if isinstance(role, Role) else role


def permissions_for_role(role: Role | str) -> list[str]:
    normalized_role = Role(role)
    return sorted(permission.value for permission in ROLE_PERMISSIONS[normalized_role])
