import base64
import hashlib
import hmac
import os

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260000


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password or not password_hash:
        return False

    try:
        algorithm, iterations, salt, expected_digest = password_hash.split("$", 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False

        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _decode(salt), int(iterations))
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(_encode(digest), expected_digest)
