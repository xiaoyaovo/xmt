from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    auth_provider: str
    provider_user_id: str | None = None
    github_id: str | None = None
    username: str
    avatar_url: str | None = None
    email: str | None = None
    last_login_at: datetime | None = None


class AuthMeResponse(BaseModel):
    authenticated: bool
    user: UserResponse | None = None


class PasswordLoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
