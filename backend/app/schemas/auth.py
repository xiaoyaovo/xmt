from datetime import datetime
import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _validate_email(value: str) -> str:
    normalized = value.strip().lower()
    if not _EMAIL_RE.fullmatch(normalized):
        raise ValueError("邮箱格式不正确")
    return normalized


EmailStr = Annotated[str, AfterValidator(_validate_email)]


class UserResponse(BaseModel):
    id: int
    auth_provider: str
    provider_user_id: str | None = None
    github_id: str | None = None
    username: str
    avatar_url: str | None = None
    email: str | None = None
    last_login_at: datetime | None = None


class AuthAccountResponse(BaseModel):
    provider: str
    provider_user_id: str | None = None
    provider_username: str | None = None
    provider_email: str | None = None
    avatar_url: str | None = None
    linked: bool
    can_unlink: bool
    linked_at: datetime | None = None
    last_used_at: datetime | None = None


class AuthAccountListResponse(BaseModel):
    accounts: list[AuthAccountResponse]


class AuthMeResponse(BaseModel):
    authenticated: bool
    user: UserResponse | None = None


class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OAuthUrlResponse(BaseModel):
    url: str


class RegisterRequestCodeIn(BaseModel):
    email: EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=64)


class PasswordForgotIn(BaseModel):
    email: EmailStr


class PasswordResetIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


class GenericOkResponse(BaseModel):
    ok: bool = True
    message: str
