import argparse
import asyncio
import getpass

from tortoise import Tortoise

from app.db.config import TORTOISE_ORM
from app.models.user import User
from app.services.auth_service import ensure_auth_account
from app.services.password_service import hash_password


async def create_password_user(email: str, password: str, username: str | None) -> User:
    normalized_email = email.strip().lower()
    if not normalized_email:
        raise ValueError("email is required")
    if not password:
        raise ValueError("password is required")

    display_username = (username or "").strip() or normalized_email.split("@", 1)[0]
    password_hash = hash_password(password)

    user = await User.get_or_none(auth_provider="password", email=normalized_email)
    if user:
        user.password_hash = password_hash
        user.provider_user_id = normalized_email
        user.email = normalized_email
        user.email_verified = True
        if username:
            user.username = display_username
        await user.save(
            update_fields=[
                "password_hash",
                "provider_user_id",
                "email",
                "email_verified",
                "username",
                "updated_at",
            ]
        )
        await ensure_auth_account(
            user,
            provider="password",
            provider_user_id=normalized_email,
            provider_username=user.username,
            provider_email=normalized_email,
            avatar_url=user.avatar_url,
            password_hash=password_hash,
        )
        return user

    user = await User.create(
        auth_provider="password",
        provider_user_id=normalized_email,
        username=display_username,
        email=normalized_email,
        email_verified=True,
        password_hash=password_hash,
    )
    await ensure_auth_account(
        user,
        provider="password",
        provider_user_id=normalized_email,
        provider_username=display_username,
        provider_email=normalized_email,
        password_hash=password_hash,
    )
    return user


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a local password login account.")
    parser.add_argument("email")
    parser.add_argument("--username", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        user = await create_password_user(args.email, password, args.username)
    finally:
        await Tortoise.close_connections()

    print(f"Password user ready: {user.email} (id={user.id})")


if __name__ == "__main__":
    asyncio.run(main())
