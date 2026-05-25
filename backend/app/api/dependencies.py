from fastapi import Header, HTTPException, status

from app.models.user import User
from app.services.jwt_service import decode_access_token


async def get_current_user(
    authorization: str | None = Header(default=None, description="Bearer access token"),
) -> User | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return await User.get_or_none(id=int(user_id))


async def require_current_user(
    authorization: str | None = Header(default=None, description="Bearer access token"),
) -> User:
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    return user
