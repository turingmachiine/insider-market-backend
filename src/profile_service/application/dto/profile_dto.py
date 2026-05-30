from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ProfileDTO:
    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None
    avatar_url: str | None
    favorite_club: str | None
    is_public: bool
    balance: Decimal
    reserved_balance: Decimal
    available_balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CreateProfileDTO:
    user_id: UUID
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    favorite_club: str | None = None
    is_public: bool = False
    initial_balance: Decimal = Decimal("1000")


@dataclass(frozen=True)
class UpdateProfileDTO:
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    favorite_club: str | None = None
    is_public: bool | None = None


@dataclass(frozen=True)
class PublicProfileDTO:
    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None
    avatar_url: str | None
    favorite_club: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime
