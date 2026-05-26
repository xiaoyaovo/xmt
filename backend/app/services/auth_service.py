from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.user import User
from app.services.jwt_service import create_access_token
from app.services.password_service import verify_password


async def authenticate_password_user(username: str, password: str) -> User:
    normalized_username = username.strip()
    if not normalized_username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入账号和密码")

    user = await User.get_or_none(auth_provider="password", username=normalized_username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    await user.save(update_fields=["last_login_at", "updated_at"])
    return user


def create_login_token(user: User) -> str:
    return create_access_token(user.id)
