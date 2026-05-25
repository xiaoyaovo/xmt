import base64
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import json
from typing import Any

from app.settings.config import settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def _b64encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode("utf-8").rstrip("=")


def _b64decode(payload: str) -> bytes:
    padding = "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(payload + padding)


def _json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def _sign(message: str) -> str:
    digest = hmac.new(settings.jwt_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return _b64encode(digest)


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    header = {
        "alg": JWT_ALGORITHM,
        "typ": "JWT",
    }
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)).timestamp()),
    }
    encoded_header = _b64encode(_json_dumps(header).encode("utf-8"))
    encoded_payload = _b64encode(_json_dumps(payload).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}"
    return f"{signing_input}.{_sign(signing_input)}"


def decode_access_token(token: str | None) -> dict[str, Any] | None:
    if not token or token.count(".") != 2:
        return None

    encoded_header, encoded_payload, signature = token.split(".")
    signing_input = f"{encoded_header}.{encoded_payload}"
    if not hmac.compare_digest(signature, _sign(signing_input)):
        return None

    try:
        header = json.loads(_b64decode(encoded_header))
        payload = json.loads(_b64decode(encoded_payload))
    except (ValueError, json.JSONDecodeError):
        return None

    if header.get("alg") != JWT_ALGORITHM:
        return None

    if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
        return None

    return payload
