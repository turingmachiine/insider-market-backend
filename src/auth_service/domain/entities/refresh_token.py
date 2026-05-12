from datetime import datetime
from uuid import UUID


class RefreshToken:
    """Persisted refresh token session."""

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None
    replaced_by_token_id: UUID | None

    def __init__(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
        revoked_at: datetime | None = None,
        replaced_by_token_id: UUID | None = None,
    ) -> None:
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked_at = revoked_at
        self.replaced_by_token_id = replaced_by_token_id

    def revoke(
        self,
        revoked_at: datetime,
        replaced_by_token_id: UUID | None = None,
    ) -> None:
        self.revoked_at = revoked_at
        self.replaced_by_token_id = replaced_by_token_id
