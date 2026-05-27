from datetime import datetime, timedelta
import hashlib
import hmac
import secrets

from fastapi import HTTPException, status
from tortoise import timezone

from app.models.user import User
from app.models.user_auth_account import UserAuthAccount
from app.models.verification_code import VerificationCode
from app.services.csv_service import purge_user_storage_dir
from app.services.jwt_service import create_access_token
from app.services.password_service import hash_password, verify_password

AUTH_PROVIDERS = ("password", "github", "linuxdo")

CODE_TTL_MINUTES = 10
CODE_MAX_ATTEMPTS = 5
RESEND_INTERVAL_SECONDS = 60
HOURLY_SEND_LIMIT = 5
DAILY_SEND_LIMIT = 10
VALID_PURPOSES = ("register", "password_reset", "bind_email")


def now_local() -> datetime:
    return timezone.now()


def _verification_expires_at(record: VerificationCode) -> datetime:
    if record.expires_at < record.created_at:
        return record.created_at + timedelta(minutes=CODE_TTL_MINUTES)
    return record.expires_at


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _verify_code_hash(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(_hash_code(code), code_hash)


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def authenticate_password_user(email: str, password: str) -> User:
    normalized_email = _normalize_email(email)
    if not normalized_email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请输入邮箱和密码")

    account = await UserAuthAccount.get_or_none(
        provider="password", provider_user_id=normalized_email
    ).prefetch_related("user")
    if account and verify_password(password, account.password_hash):
        await mark_login_used(account)
        return account.user

    legacy_user = await User.get_or_none(auth_provider="password", email=normalized_email)
    if not legacy_user or not verify_password(password, legacy_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")

    account = await ensure_auth_account(
        legacy_user,
        provider="password",
        provider_user_id=normalized_email,
        provider_username=legacy_user.username,
        provider_email=normalized_email,
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
    now = now_local()
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
    now = now_local()
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
        user.email_verified = True
        if github_id is not None:
            user.github_id = github_id
        await user.save(
            update_fields=["username", "avatar_url", "email", "email_verified", "github_id", "updated_at"]
        )
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
            email_verified=True,
            last_login_at=now_local(),
        )
    else:
        user.auth_provider = provider
        user.provider_user_id = provider_user_id
        if github_id is not None:
            user.github_id = github_id
        user.username = username
        user.avatar_url = avatar_url
        user.email = email
        user.email_verified = True
        user.last_login_at = now_local()
        await user.save(
            update_fields=[
                "auth_provider",
                "provider_user_id",
                "github_id",
                "username",
                "avatar_url",
                "email",
                "email_verified",
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


async def delete_user_account(user: User) -> None:
    accounts = await UserAuthAccount.filter(user=user)
    emails = {value.strip().lower() for value in [user.email, *(account.provider_email for account in accounts)] if value}
    for email in emails:
        await VerificationCode.filter(email=email).delete()

    await user.delete()
    purge_user_storage_dir(user)


async def _enforce_send_rate_limits(email: str, purpose: str) -> None:
    now = now_local()
    last = (
        await VerificationCode.filter(email=email, purpose=purpose)
        .order_by("-created_at")
        .first()
    )
    if last and (now - last.created_at) < timedelta(seconds=RESEND_INTERVAL_SECONDS):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送过于频繁,请稍后再试",
        )

    hourly_count = await VerificationCode.filter(
        email=email,
        purpose=purpose,
        created_at__gte=now - timedelta(hours=1),
    ).count()
    if hourly_count >= HOURLY_SEND_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="该邮箱发送次数过多,请稍后再试",
        )

    daily_count = await VerificationCode.filter(
        email=email,
        purpose=purpose,
        created_at__gte=now - timedelta(days=1),
    ).count()
    if daily_count >= DAILY_SEND_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="该邮箱今日发送次数已达上限",
        )


async def create_verification_code(email: str, purpose: str) -> str:
    if purpose not in VALID_PURPOSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码用途无效")

    normalized = _normalize_email(email)
    await _enforce_send_rate_limits(normalized, purpose)

    code = _generate_code()
    expires_at = now_local() + timedelta(minutes=CODE_TTL_MINUTES)
    await VerificationCode.create(
        email=normalized,
        code_hash=_hash_code(code),
        purpose=purpose,
        expires_at=expires_at,
    )
    return code


async def verify_code(email: str, code: str, purpose: str) -> VerificationCode:
    normalized = _normalize_email(email)
    now = now_local()
    record = (
        await VerificationCode.filter(
            email=normalized,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码无效或已过期")

    if _verification_expires_at(record) < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码无效或已过期")

    if record.attempts >= CODE_MAX_ATTEMPTS:
        record.consumed_at = now
        await record.save(update_fields=["consumed_at", "updated_at"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误次数过多,请重新申请")

    if not _verify_code_hash(code, record.code_hash):
        record.attempts += 1
        update_fields = ["attempts", "updated_at"]
        if record.attempts >= CODE_MAX_ATTEMPTS:
            record.consumed_at = now
            update_fields.append("consumed_at")
        await record.save(update_fields=update_fields)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误")

    return record


async def _consume_code(record: VerificationCode) -> None:
    record.consumed_at = now_local()
    await record.save(update_fields=["consumed_at", "updated_at"])


async def consume_verification_code(email: str, purpose: str) -> None:
    normalized = _normalize_email(email)
    record = (
        await VerificationCode.filter(
            email=normalized,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )
    if record:
        await _consume_code(record)


async def register_with_code(
    *,
    email: str,
    code: str,
    password: str,
    username: str | None = None,
) -> User:
    normalized = _normalize_email(email)

    existing_account = await UserAuthAccount.get_or_none(
        provider="password", provider_user_id=normalized
    )
    if existing_account:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已注册")

    record = await verify_code(normalized, code, "register")

    now = now_local()
    display_username = (username or "").strip() or normalized.split("@", 1)[0]
    password_hash = hash_password(password)

    user = await User.create(
        auth_provider="password",
        provider_user_id=normalized,
        username=display_username,
        email=normalized,
        email_verified=True,
        password_hash=password_hash,
        last_login_at=now,
    )
    await ensure_auth_account(
        user,
        provider="password",
        provider_user_id=normalized,
        provider_username=display_username,
        provider_email=normalized,
        password_hash=password_hash,
    )
    await _consume_code(record)
    return user


async def _ensure_email_can_bind(user: User, normalized: str) -> None:
    existing_password_account = await UserAuthAccount.get_or_none(provider="password", provider_user_id=normalized)
    if existing_password_account and existing_password_account.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已绑定到其他账号")
    if existing_password_account and existing_password_account.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前账号已绑定邮箱登录")

    email_owner = await User.get_or_none(email=normalized)
    if email_owner and email_owner.id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已绑定到其他账号")

    current_password_account = await UserAuthAccount.get_or_none(user=user, provider="password")
    if current_password_account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前账号已绑定邮箱登录")


async def request_bind_email(user: User, email: str) -> str:
    normalized = _normalize_email(email)
    await _ensure_email_can_bind(user, normalized)
    return await create_verification_code(normalized, "bind_email")


async def bind_email_login(user: User, *, email: str, code: str, password: str) -> UserAuthAccount:
    normalized = _normalize_email(email)
    await _ensure_email_can_bind(user, normalized)

    record = await verify_code(normalized, code, "bind_email")
    password_hash = hash_password(password)
    account = await ensure_auth_account(
        user,
        provider="password",
        provider_user_id=normalized,
        provider_username=user.username,
        provider_email=normalized,
        password_hash=password_hash,
    )

    user.email = normalized
    user.email_verified = True
    user.password_hash = password_hash
    if not user.provider_user_id:
        user.provider_user_id = normalized
    await user.save(update_fields=["email", "email_verified", "password_hash", "provider_user_id", "updated_at"])
    await _consume_code(record)
    return account


async def request_password_reset(email: str) -> None:
    normalized = _normalize_email(email)
    # Always create the code row so timing/rate-limit behavior is identical
    # regardless of whether the email is registered (anti-enumeration).
    code = await create_verification_code(normalized, "password_reset")

    user_exists = await User.filter(email=normalized).exists() or await UserAuthAccount.filter(
        provider="password", provider_user_id=normalized
    ).exists()
    if not user_exists:
        return

    # Import locally to avoid import cycles at module load time.
    from app.services.email_service import send_password_reset_code

    await send_password_reset_code(to=normalized, code=code)


async def reset_password(*, email: str, code: str, new_password: str) -> None:
    normalized = _normalize_email(email)
    record = await verify_code(normalized, code, "password_reset")

    account = await UserAuthAccount.get_or_none(
        provider="password", provider_user_id=normalized
    ).prefetch_related("user")
    user = account.user if account else await User.get_or_none(email=normalized)
    if not user:
        # Consume the code anyway to avoid abuse, then return a generic error.
        await _consume_code(record)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码无效或已过期")

    password_hash = hash_password(new_password)
    user.password_hash = password_hash
    await user.save(update_fields=["password_hash", "updated_at"])

    await ensure_auth_account(
        user,
        provider="password",
        provider_user_id=normalized,
        provider_username=user.username,
        provider_email=normalized,
        password_hash=password_hash,
    )
    await _consume_code(record)
