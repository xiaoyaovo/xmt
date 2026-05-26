from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.user import User
from app.models.user_auth_account import UserAuthAccount
from app.services.jwt_service import create_access_token
from app.services.password_service import verify_password

AUTH_PROVIDERS = ("password", "github", "linuxdo")


def now_naive_utc() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


async def authenticate_password_user(username: str, password: str) -> User:
    normalized_username = username.strip()
    if not normalized_username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入账号和密码")

    account = await UserAuthAccount.get_or_none(provider="password", provider_user_id=normalized_username).prefetch_related(
        "user"
    )
    if account and verify_password(password, account.password_hash):
        await mark_login_used(account)
        return account.user

    legacy_user = await User.get_or_none(auth_provider="password", username=normalized_username)
    if not legacy_user or not verify_password(password, legacy_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    account = await ensure_auth_account(
        legacy_user,
        provider="password",
        provider_user_id=normalized_username,
        provider_username=normalized_username,
        provider_email=legacy_user.email,
        avatar_url=legacy_user.avatar_url,
        password_hash=legacy_user.password_hash,
    )
    await mark_login_used(account)
    return legacy_user


def create_login_token(user: User) -> str:
    return create_access_token(user.id)


async def ensure_auth_account(
    user: User,
    *,
    provider: str,
    provider_user_id: str,
    provider_username: str | None = None,
    provider_email: str | None = None,
    avatar_url: str | None = None,
    password_hash: str | None = None,
) -> UserAuthAccount:
    now = now_naive_utc()
    account, created = await UserAuthAccount.get_or_create(
        provider=provider,
        provider_user_id=provider_user_id,
        defaults={
            "user": user,
            "provider_username": provider_username,
            "provider_email": provider_email,
            "avatar_url": avatar_url,
            "password_hash": password_hash,
            "linked_at": now,
        },
    )
    if account.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该登录方式已绑定到其他账号")

    update_fields: list[str] = []
    for field_name, value in {
        "provider_username": provider_username,
        "provider_email": provider_email,
        "avatar_url": avatar_url,
        "password_hash": password_hash,
    }.items():
        if value is not None and getattr(account, field_name) != value:
            setattr(account, field_name, value)
            update_fields.append(field_name)

    if created and account.linked_at is None:
        account.linked_at = now
        update_fields.append("linked_at")

    if update_fields:
        update_fields.append("updated_at")
        await account.save(update_fields=update_fields)

    return account


async def mark_login_used(account: UserAuthAccount) -> None:
    now = now_naive_utc()
    account.last_used_at = now
    account.user.last_login_at = now
    await account.save(update_fields=["last_used_at", "updated_at"])
    await account.user.save(update_fields=["last_login_at", "updated_at"])


async def get_or_create_oauth_user(
    *,
    provider: str,
    provider_user_id: str,
    username: str,
    avatar_url: str | None = None,
    email: str | None = None,
    github_id: str | None = None,
) -> User:
    account = await UserAuthAccount.get_or_none(
        provider=provider,
        provider_user_id=provider_user_id,
    ).prefetch_related("user")
    if account:
        user = account.user
        user.username = username
        user.avatar_url = avatar_url
        user.email = email
        if github_id is not None:
            user.github_id = github_id
        await user.save(update_fields=["username", "avatar_url", "email", "github_id", "updated_at"])
        await ensure_auth_account(
            user,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=username,
            provider_email=email,
            avatar_url=avatar_url,
        )
        await mark_login_used(account)
        return user

    legacy_filters = {"github_id": provider_user_id} if provider == "github" else {
        "auth_provider": provider,
        "provider_user_id": provider_user_id,
    }
    user = await User.get_or_none(**legacy_filters)
    if user is None:
        user = await User.create(
            auth_provider=provider,
            provider_user_id=provider_user_id,
            github_id=github_id,
            username=username,
            avatar_url=avatar_url,
            email=email,
            last_login_at=now_naive_utc(),
        )
    else:
        user.auth_provider = provider
        user.provider_user_id = provider_user_id
        if github_id is not None:
            user.github_id = github_id
        user.username = username
        user.avatar_url = avatar_url
        user.email = email
        user.last_login_at = now_naive_utc()
        await user.save(
            update_fields=[
                "auth_provider",
                "provider_user_id",
                "github_id",
                "username",
                "avatar_url",
                "email",
                "last_login_at",
                "updated_at",
            ]
        )

    account = await ensure_auth_account(
        user,
        provider=provider,
        provider_user_id=provider_user_id,
        provider_username=username,
        provider_email=email,
        avatar_url=avatar_url,
    )
    await mark_login_used(account)
    return user


async def link_oauth_account(
    user: User,
    *,
    provider: str,
    provider_user_id: str,
    username: str,
    avatar_url: str | None = None,
    email: str | None = None,
    github_id: str | None = None,
) -> UserAuthAccount:
    existing = await UserAuthAccount.get_or_none(provider=provider, provider_user_id=provider_user_id)
    if existing and existing.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该登录方式已绑定到其他账号")

    account = await ensure_auth_account(
        user,
        provider=provider,
        provider_user_id=provider_user_id,
        provider_username=username,
        provider_email=email,
        avatar_url=avatar_url,
    )

    user.username = user.username or username
    if not user.avatar_url:
        user.avatar_url = avatar_url
    if not user.email:
        user.email = email
    if provider == "github":
        user.github_id = github_id or provider_user_id
    await user.save(update_fields=["username", "avatar_url", "email", "github_id", "updated_at"])
    return account


async def list_auth_accounts(user: User) -> list[UserAuthAccount]:
    return await UserAuthAccount.filter(user=user).order_by("provider")


async def unlink_auth_account(user: User, provider: str) -> None:
    if provider == "password":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="暂不支持解绑账号密码登录")

    account = await UserAuthAccount.get_or_none(user=user, provider=provider)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="登录方式未绑定")

    account_count = await UserAuthAccount.filter(user=user).count()
    if account_count <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="至少保留一种登录方式")

    await account.delete()
    if provider == "github" and user.github_id == account.provider_user_id:
        user.github_id = None
        await user.save(update_fields=["github_id", "updated_at"])
