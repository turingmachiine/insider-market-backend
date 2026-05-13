from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
    permissions: list[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirmRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=12, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


class UserRoleGrantRequest(BaseModel):
    role_name: str = Field(min_length=2, max_length=100)


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    permissions: list[str] = Field(default_factory=list)


class RolePermissionsUpdateRequest(BaseModel):
    permissions: list[str]


class RoleResponse(BaseModel):
    name: str
    permissions: list[str]


class PermissionCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)


class PermissionResponse(BaseModel):
    name: str


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
