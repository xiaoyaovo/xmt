from functools import lru_cache
from pathlib import Path

import httpx
from fastapi import HTTPException, status

from app.settings.config import settings

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"
RESEND_ENDPOINT = "https://api.resend.com/emails"
HTTP_TIMEOUT_SECONDS = 10.0


@lru_cache(maxsize=8)
def _load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    return path.read_text(encoding="utf-8")


def _render_template(name: str, *, code: str) -> str:
    # Templates contain CSS braces, so we use replace() instead of str.format().
    return _load_template(name).replace("{code}", code)


async def send_email(*, to: str, subject: str, html: str) -> str:
    if not settings.resend_api_key or not settings.mail_from_email:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="邮件服务未配置",
        )

    payload = {
        "from": f"{settings.mail_from_name} <{settings.mail_from_email}>",
        "to": [to],
        "subject": subject,
        "html": html,
    }
    headers = {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(RESEND_ENDPOINT, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="邮件发送失败",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="邮件发送失败",
        )

    data = response.json()
    return str(data.get("id") or "")


async def send_verification_code(*, to: str, code: str) -> str:
    html = _render_template("verification_code.html", code=code)
    subject = f"【{settings.mail_from_name}】你的注册验证码是 {code}"
    return await send_email(to=to, subject=subject, html=html)


async def send_password_reset_code(*, to: str, code: str) -> str:
    html = _render_template("password_reset.html", code=code)
    subject = f"【{settings.mail_from_name}】重置密码验证码"
    return await send_email(to=to, subject=subject, html=html)
