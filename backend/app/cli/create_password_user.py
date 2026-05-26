import argparse
import asyncio
import getpass

from tortoise import Tortoise

from app.db.config import TORTOISE_ORM
from app.models.user import User
from app.services.auth_service import ensure_auth_account
from app.services.password_service import hash_password


async def create_password_user(username: str, password: str, email: str | None) -> User:
    normalized_username = username.strip()
    if not normalized_username:
        raise ValueError("username is required")
    if not password:
        raise ValueError("password is required")

    user = await User.get_or_none(auth_provider="password", username=normalized_username)
    password_hash = hash_password(password)
    if user:
        user.password_hash = password_hash
        user.provider_user_id = normalized_username
        update_fields = ["password_hash", "provider_user_id", "updated_at"]
        if email is not None:
            user.email = email
            update_fields.append("email")
        await user.save(update_fields=update_fields)
        await ensure_auth_account(
            user,
            provider="password",
            provider_user_id=normalized_username,
            provider_username=normalized_username,
            provider_email=user.email,
            avatar_url=user.avatar_url,
            password_hash=password_hash,
        )
        return user

    user = await User.create(
        auth_provider="password",
        provider_user_id=normalized_username,
        username=normalized_username,
        email=email,
        password_hash=password_hash,
    )
    await ensure_auth_account(
        user,
        provider="password",
        provider_user_id=normalized_username,
        provider_username=normalized_username,
        provider_email=email,
        password_hash=password_hash,
    )
    return user


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a local password login account.")
    parser.add_argument("username")
    parser.add_argument("--email", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        user = await create_password_user(args.username, password, args.email)
    finally:
        await Tortoise.close_connections()

    print(f"Password user ready: {user.username} (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())
