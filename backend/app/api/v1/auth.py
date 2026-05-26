import base64
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlencode
from urllib.request import Request as UrlRequest, urlopen
import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import AuthMeResponse, LoginResponse, PasswordLoginRequest, UserResponse
from app.services.auth_service import authenticate_password_user, create_login_token
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


def _parse_oauth_state(state: str) -> tuple[str, str]:
    state_values = parse_qs(state)
    safe_redirect = _safe_redirect_path(state_values.get("redirect", [state])[0])
    frontend_origin = _safe_frontend_origin(state_values.get("frontend_origin", [""])[0])
    return safe_redirect, frontend_origin


def _callback_redirect(user: User, state: str) -> RedirectResponse:
    safe_redirect, frontend_origin = _parse_oauth_state(state)
    token_query = urlencode({"access_token": create_login_token(user), "redirect": safe_redirect})
    return RedirectResponse(
        f"{frontend_origin}/#/auth/callback?{token_query}",
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


@router.post("/login", response_model=LoginResponse, summary="Login with username and password")
async def password_login(payload: PasswordLoginRequest) -> LoginResponse:
    user = await authenticate_password_user(payload.username, payload.password)
    return LoginResponse(access_token=create_login_token(user), user=serialize_user(user))


@router.get("/github/login", summary="Start GitHub OAuth login")
async def github_login(
    request: Request,
    redirect: str = "/tools",
    frontend_origin: str = "",
) -> RedirectResponse:
    if not settings.github_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GitHub OAuth is not configured")

    safe_redirect = _safe_redirect_path(redirect)
    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = urlencode({"redirect": safe_redirect, "frontend_origin": safe_frontend_origin})
    query = urlencode(
        {
            "client_id": settings.github_client_id,
            "redirect_uri": str(request.url_for("github_callback")),
            "scope": "read:user user:email",
            "state": state,
        }
    )
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{query}", status_code=status.HTTP_302_FOUND)


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

    user, _ = await User.update_or_create(
        defaults={
            "auth_provider": "github",
            "provider_user_id": str(profile["id"]),
            "username": profile.get("login") or f"github-{profile['id']}",
            "avatar_url": profile.get("avatar_url"),
            "email": primary_email,
            "last_login_at": datetime.now(UTC).replace(tzinfo=None),
        },
        github_id=str(profile["id"]),
    )

    return _callback_redirect(user, state)


@router.get("/linuxdo/login", summary="Start LinuxDo OAuth login")
async def linuxdo_login(
    request: Request,
    redirect: str = "/tools",
    frontend_origin: str = "",
) -> RedirectResponse:
    if not settings.linuxdo_client_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LinuxDo OAuth is not configured")

    safe_redirect = _safe_redirect_path(redirect)
    safe_frontend_origin = _require_allowed_frontend_origin(frontend_origin)
    state = urlencode({"redirect": safe_redirect, "frontend_origin": safe_frontend_origin})
    query = urlencode(
        {
            "client_id": settings.linuxdo_client_id,
            "redirect_uri": str(request.url_for("linuxdo_callback")),
            "response_type": "code",
            "scope": "read",
            "state": state,
        }
    )
    return RedirectResponse(f"{settings.linuxdo_authorize_url}?{query}", status_code=status.HTTP_302_FOUND)


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

    user, _ = await User.update_or_create(
        defaults={
            "github_id": None,
            "username": username,
            "avatar_url": _linuxdo_avatar_url(profile),
            "email": profile.get("email"),
            "last_login_at": datetime.now(UTC).replace(tzinfo=None),
        },
        auth_provider="linuxdo",
        provider_user_id=str(profile_id),
    )

    return _callback_redirect(user, state)


@router.get("/me", response_model=AuthMeResponse, summary="Get current user")
async def get_me(user: User | None = Depends(get_current_user)) -> AuthMeResponse:
    return AuthMeResponse(authenticated=bool(user), user=serialize_user(user) if user else None)


@router.post("/logout", summary="Logout")
async def logout(response: Response) -> dict[str, bool]:
    return {"ok": True}
