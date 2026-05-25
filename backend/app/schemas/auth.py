from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    github_id: str
    username: str
    avatar_url: str | None = None
    email: str | None = None
    last_login_at: datetime | None = None


class AuthMeResponse(BaseModel):
    authenticated: bool
    user: UserResponse | None = None

