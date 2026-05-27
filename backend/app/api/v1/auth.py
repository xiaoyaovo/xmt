import base64
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen
import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_current_user, require_current_user
from app.models.user import User
from app.models.user_auth_account import UserAuthAccount
from app.schemas.auth import (
    AuthAccountListResponse,
    AuthAccountResponse,
    AuthMeResponse,
    GenericOkResponse,
    LoginResponse,
    OAuthUrlResponse,
    PasswordForgotIn,
    PasswordLoginRequest,
    PasswordResetIn,
    RegisterIn,
    RegisterRequestCodeIn,
    UserResponse,
)
from app.services.auth_service import (
    AUTH_PROVIDERS,
    authenticate_password_user,
    create_login_token,
    create_verification_code,
    get_or_create_oauth_user,
    link_oauth_account,
    list_auth_accounts,
    register_with_code,
    request_password_reset,
    reset_password,
    unlink_auth_account,
)
from app.services.email_service import send_verification_code
from app.services.jwt_service import create_signed_payload, decode_signed_payload
from app.settings.config import settings

router = APIRouter(prefix="/auth")


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        auth_provider=user.auth_provider,
        provider_user_id=user.provider_user_id,
        github_id=user.github_id,
        username=user.username,
        avatar_url=user.avatar_url,
        email=user.email,
        last_login_at=user.last_login_at,
    )


def serialize_auth_account(account: UserAuthAccount, *, can_unlink: bool) -> AuthAccountResponse:
    return AuthAccountResponse(
        provider=account.provider,
        provider_user_id=account.provider_user_id,
        provider_username=account.provider_username,
        provider_email=account.provider_email,
        avatar_url=account.avatar_url,
        linked=True,
        can_unlink=can_unlink,
        linked_at=account.linked_at,
        last_used_at=account.last_used_at,
    )


def _github_request(url: str, *, method: str = "GET", body: dict | None = None, token: str | None = None) -> dict:
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": "xinming-tools",
    }

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = UrlRequest(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _oauth_request(
    url: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    token: str | None = None,
    basic_auth: tuple[str, str] | None = None,
) -> dict:
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": "xinming-tools",
    }

    if body is not None:
        data = urlencode(body).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if basic_auth:
        client_id, client_secret = basic_auth
        encoded_credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {encoded_credentials}"

    request = UrlRequest(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _safe_redirect_path(value: str) -> str:
    return value if value.startswith("/") and not value.startswith("//") else "/tools"


def _safe_frontend_origin(value: str) -> str:
    origin = value.rstrip("/")
    if origin in settings.cors_origin_list:
        return origin

    return settings.frontend_url.rstrip("/")


def _require_allowed_frontend_origin(value: str) -> str:
    origin = value.rstrip("/") if value else settings.frontend_url.rstrip("/")
    if origin not in settings.cors_origin_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Frontend origin is not allowed")

    return origin


def _create_oauth_state(
    *,
    purpose: str,
    redirect: str,
    frontend_origin: str,
    user_id: int | None = None,
) -> str:
    payload = {
        "purpose": purpose,
        "redirect": _safe_redirect_path(redirect),
        "frontend_origin": _safe_frontend_origin(frontend_origin),
        "iat": int(datetime.now(UTC).timestamp()),
        "exp": int((datetime.now(UTC) + timedelta(minutes=15)).timestamp()),
    }
    if user_id is not None:
        payload["user_id"] = user_id

    return create_signed_payload(payload)


def _parse_oauth_state(state: str) -> dict:
    payload = decode_signed_payload(state)
    if payload:
        payload["redirect"] = _safe_redirect_path(str(payload.get("redirect") or "/tools"))
        payload["frontend_origin"] = _safe_frontend_origin(str(payload.get("frontend_origin") or ""))
        payload["purpose"] = payload.get("purpose") or "login"
        return payload

    return {
        "purpose": "login",
        "redirect": _safe_redirect_path(state),
        "frontend_origin": settings.frontend_url.rstrip("/"),
    }


def _callback_redirect(user: User, state: str) -> RedirectResponse:
    state_payload = _parse_oauth_state(state)
    token_query = urlencode({"access_token": create_login_token(user), "redirect": state_payload["redirect"]})
    return RedirectResponse(
        f"{state_payload['frontend_origin']}/#/auth/callback?{token_query}",
        status_code=status.HTTP_302_FOUND,
    )


def _link_callback_redirect(
    state: str,
    *,
    provider: str,
    status_value: str = "linked",
    message: str | None = None,
) -> RedirectResponse:
    state_payload = _parse_oauth_state(state)
    query_payload = {
        "provider": provider,
        "provider_status": status_value,
        "redirect": state_payload["redirect"],
    }
    if message:
        query_payload["message"] = message
    query = urlencode(query_payload)
    return RedirectResponse(
        f"{state_payload['frontend_origin']}/#/auth/callback?{query}",
        status_code=status.HTTP_302_FOUND,
    )


def _linuxdo_avatar_url(profile: dict) -> str | None:
    avatar_url = profile.get("avatar_url") or profile.get("avatar") or profile.get("picture")
    if avatar_url:
        return avatar_url

    avatar_template = profile.get("avatar_template")
    if isinstance(avatar_template, str):
        return avatar_template.replace("{size}", "288")

    return None


def _github_profile_values(profile: dict, email: str | None) -> dict:
    profile_id = str(profile["id"])
    return {
        "provider": "github",
        "provider_user_id": profile_id,
        "username": profile.get("login") or f"github-{profile_id}",
        "avatar_url": profile.get("avatar_url"),
        "email": email,
        "github_id": profile_id,
    }


def _linuxdo_profile_values(profile: dict) -> dict:
    profile_id = profile.get("id") or profile.get("sub") or profile.get("user_id")
    if profile_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="LinuxDo user profile is invalid")
    if profile.get("active") is False or profile.get("silenced") is True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="LinuxDo account is not allowed")

    username = (
        profile.get("username")
        or profile.get("login")
        or profile.get("name")
        or profile.get("nickname")
        or f"linuxdo-{profile_id}"
    )
    return {
        "provider": "linuxdo",
        "provider_user_id": str(profile_id),
        "username": username,
        "avatar_url": _linuxdo_avatar_url(profile),
        "email": profile.get("email"),
        "github_id": None,
    }


def _github_authorize_url(request: Request, state: str, *, prompt: str | None = None) -> str:
    query_params = {
        "client_id": settings.github_client_id,
        "redirect_uri": str(request.url_for("github_callback")),
        "scope": "read:user user:email",
        "state": state,
    }
    if prompt == "select_account":
        query_params["prompt"] = prompt

    query = urlencode(query_params)
    return f"https://github.com/login/oauth/authorize?{query}"


def _linuxdo_authorize_url(request: Request, state: str) -> str:
    query = urlencode(
        {
            "client_id": settings.linuxdo_client_id,
            "redirect_uri": str(request.url_for("linuxdo_callback")),
            "response_type": "code",
            "scope": "read",
            "state": state,
        }
    )
    return f"{settings.linuxdo_authorize_url}?{query}"


@router.post("/login", response_model=LoginResponse, summary="Login with email and password")
async def password_login(payload: PasswordLoginRequest) -> LoginResponse:
    user = await authenticate_password_user(payload.email, payload.password)
    return LoginResponse(access_token=create_login_token(user), user=serialize_user(user))


@router.post(
    "/register/request-code",
    response_model=GenericOkResponse,
    summary="Send a registration verification code",
)
async def register_request_code(payload: RegisterRequestCodeIn) -> GenericOkResponse:
    try:
        code = await create_verification_code(payload.email, "register")
        await send_verification_code(to=payload.email, code=code)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise
        # Don't leak email-delivery details to clients.
        return GenericOkResponse(message="如该邮箱可注册,验证码已发送")

    return GenericOkResponse(message="如该邮箱可注册,验证码已发送")


@router.post("/register", response_model=LoginResponse, summary="Complete registration with code")
async def register(payload: RegisterIn) -> LoginResponse:
    user = await register_with_code(
        email=payload.email,
        code=payload.code,
        password=payload.password,
        username=payload.username,
    )
    return LoginResponse(access_token=create_login_token(user), user=serialize_user(user))


@router.post(
    "/password/forgot",
    response_model=GenericOkResponse,
    summary="Request a password reset verification code",
)
async def password_forgot(payload: PasswordForgotIn) -> GenericOkResponse:
    try:
        await request_password_reset(payload.email)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise
        # Anti-enumeration: hide all other errors behind a generic success.
        return GenericOkResponse(message="如该邮箱已注册,验证码已发送")

    return GenericOkResponse(message="如该邮箱已注册,验证码已发送")


@router.post(
    "/password/reset",
    response_model=GenericOkResponse,
    summary="Reset password with verification code",
)
async def password_reset(payload: PasswordResetIn) -> GenericOkResponse:
    await reset_password(email=payload.email, code=payload.code, new_password=payload.new_password)
    return GenericOkResponse(message="密码已重置,请使用新密码登录")


@router.get("/github/login", summary="Start GitHub OAuth login")
async def github_login(
    request: Request,
    redirect: str = "/tools",
    frontend_origin: str = "",
) -> RedirectResponse:
    if not settings.github_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GitHub OAuth is not configured")

    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = _create_oauth_state(purpose="login", redirect=redirect, frontend_origin=safe_frontend_origin)
    return RedirectResponse(_github_authorize_url(request, state), status_code=status.HTTP_302_FOUND)


@router.get("/github/callback", summary="Handle GitHub OAuth callback")
async def github_callback(code: str, state: str = "/tools") -> RedirectResponse:
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GitHub OAuth is not configured")

    token_response = _github_request(
        "https://github.com/login/oauth/access_token",
        method="POST",
        body={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
        },
    )
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GitHub login failed")

    profile = _github_request("https://api.github.com/user", token=access_token)
    emails = _github_request("https://api.github.com/user/emails", token=access_token)
    primary_email = next((item.get("email") for item in emails if item.get("primary")), None)
    profile_values = _github_profile_values(profile, primary_email)
    state_payload = _parse_oauth_state(state)

    if state_payload.get("purpose") == "link":
        user = await User.get_or_none(id=int(state_payload.get("user_id", 0)))
        if not user:
            return _link_callback_redirect(
                state,
                provider="github",
                status_value="auth_required",
                message="登录状态已失效，请重新登录后再绑定 GitHub。",
            )
        try:
            await link_oauth_account(user, **profile_values)
        except HTTPException as exc:
            if exc.status_code == status.HTTP_409_CONFLICT:
                return _link_callback_redirect(
                    state,
                    provider="github",
                    status_value="conflict",
                    message="这个 GitHub 已经绑定到另一个账号。请先登录那个账号解绑，或换一个 GitHub 账号。",
                )
            raise
        return _link_callback_redirect(state, provider="github")

    user = await get_or_create_oauth_user(**profile_values)
    return _callback_redirect(user, state)


@router.get("/github/link", response_model=OAuthUrlResponse, summary="Start GitHub OAuth account linking")
async def github_link(
    request: Request,
    redirect: str = "/account/security",
    frontend_origin: str = "",
    prompt: str = "",
    user: User = Depends(require_current_user),
) -> RedirectResponse:
    if not settings.github_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GitHub OAuth is not configured")

    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = _create_oauth_state(
        purpose="link",
        redirect=redirect,
        frontend_origin=safe_frontend_origin,
        user_id=user.id,
    )
    github_prompt = "select_account" if prompt == "select_account" else None
    return OAuthUrlResponse(url=_github_authorize_url(request, state, prompt=github_prompt))


@router.get("/linuxdo/login", summary="Start LinuxDo OAuth login")
async def linuxdo_login(
    request: Request,
    redirect: str = "/tools",
    frontend_origin: str = "",
) -> RedirectResponse:
    if not settings.linuxdo_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LinuxDo OAuth is not configured")

    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = _create_oauth_state(purpose="login", redirect=redirect, frontend_origin=safe_frontend_origin)
    return RedirectResponse(_linuxdo_authorize_url(request, state), status_code=status.HTTP_302_FOUND)


@router.get("/linuxdo/callback", summary="Handle LinuxDo OAuth callback")
async def linuxdo_callback(request: Request, code: str, state: str = "/tools") -> RedirectResponse:
    if not settings.linuxdo_client_id or not settings.linuxdo_client_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LinuxDo OAuth is not configured")

    token_response = _oauth_request(
        settings.linuxdo_token_url,
        method="POST",
        body={
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": str(request.url_for("linuxdo_callback")),
        },
        basic_auth=(settings.linuxdo_client_id, settings.linuxdo_client_secret),
    )
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="LinuxDo login failed")

    profile = _oauth_request(settings.linuxdo_user_url, token=access_token)
    profile_values = _linuxdo_profile_values(profile)
    state_payload = _parse_oauth_state(state)

    if state_payload.get("purpose") == "link":
        user = await User.get_or_none(id=int(state_payload.get("user_id", 0)))
        if not user:
            return _link_callback_redirect(
                state,
                provider="linuxdo",
                status_value="auth_required",
                message="登录状态已失效，请重新登录后再绑定 LinuxDo。",
            )
        try:
            await link_oauth_account(user, **profile_values)
        except HTTPException as exc:
            if exc.status_code == status.HTTP_409_CONFLICT:
                return _link_callback_redirect(
                    state,
                    provider="linuxdo",
                    status_value="conflict",
                    message="这个 LinuxDo 已经绑定到另一个账号。请先登录那个账号解绑，或换一个 LinuxDo 账号。",
                )
            raise
        return _link_callback_redirect(state, provider="linuxdo")

    user = await get_or_create_oauth_user(**profile_values)
    return _callback_redirect(user, state)


@router.get("/linuxdo/link", response_model=OAuthUrlResponse, summary="Start LinuxDo OAuth account linking")
async def linuxdo_link(
    request: Request,
    redirect: str = "/account/security",
    frontend_origin: str = "",
    user: User = Depends(require_current_user),
) -> RedirectResponse:
    if not settings.linuxdo_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LinuxDo OAuth is not configured")

    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = _create_oauth_state(
        purpose="link",
        redirect=redirect,
        frontend_origin=safe_frontend_origin,
        user_id=user.id,
    )
    return OAuthUrlResponse(url=_linuxdo_authorize_url(request, state))


@router.get("/accounts", response_model=AuthAccountListResponse, summary="List linked login methods")
async def get_auth_accounts(user: User = Depends(require_current_user)) -> AuthAccountListResponse:
    accounts = await list_auth_accounts(user)
    account_count = len(accounts)
    account_by_provider = {account.provider: account for account in accounts}
    response_accounts: list[AuthAccountResponse] = []
    for provider in AUTH_PROVIDERS:
        account = account_by_provider.get(provider)
        if account:
            response_accounts.append(
                serialize_auth_account(account, can_unlink=provider != "password" and account_count > 1)
            )
            continue

        response_accounts.append(
            AuthAccountResponse(
                provider=provider,
                linked=False,
                can_unlink=False,
            )
        )

    return AuthAccountListResponse(accounts=response_accounts)


@router.delete("/accounts/{provider}", summary="Unlink a login method")
async def delete_auth_account(provider: str, user: User = Depends(require_current_user)) -> dict[str, bool]:
    if provider not in AUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="登录方式不存在")

    await unlink_auth_account(user, provider)
    return {"ok": True}


@router.get("/me", response_model=AuthMeResponse, summary="Get current user")
async def get_me(user: User | None = Depends(get_current_user)) -> AuthMeResponse:
    return AuthMeResponse(authenticated=bool(user), user=serialize_user(user) if user else None)


@router.post("/logout", summary="Logout")
async def logout(response: Response) -> dict[str, bool]:
    return {"ok": True}
