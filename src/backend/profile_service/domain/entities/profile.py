from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.backend.profile_service.core.utils.datetime_utils import utc_now


@dataclass
class Profile:
    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    favorite_club: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.display_name = self.display_name.strip()
        if not self.display_name:
            raise ValueError("Display name must not be empty")

    def update(
        self,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = None,
        favorite_club: str | None = None,
    ) -> None:
        if display_name is not None:
            display_name = display_name.strip()
            if not display_name:
                raise ValueError("Display name must not be empty")
            self.display_name = display_name
        if bio is not None:
            self.bio = bio
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if favorite_club is not None:
            self.favorite_club = favorite_club
        self.updated_at = utc_now()
