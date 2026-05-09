from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.common.domain.security import Role


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class RegisterResponse(BaseModel):
    user_id: UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
    permissions: list[str]


class UserRoleGrantRequest(BaseModel):
    role_name: Role


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    roles: list[str]
    permissions: list[str]
    created_at: datetime | None = None


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int
