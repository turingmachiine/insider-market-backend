from datetime import datetime
from uuid import UUID


class PasswordResetToken:
    """Persisted single-use password reset token."""

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    used_at: datetime | None

    def __init__(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        used_at: datetime | None = None,
    ) -> None:
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.used_at = used_at

    def is_usable(self, now: datetime) -> bool:
        return self.used_at is None and self.expires_at > now

    def mark_used(self, used_at: datetime) -> None:
        self.used_at = used_at
