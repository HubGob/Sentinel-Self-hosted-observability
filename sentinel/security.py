"""Password hashing and JWT issuing/verification.

Two deliberate choices worth knowing about:

- **bcrypt directly, not passlib.** passlib is unmaintained and breaks against
  bcrypt 4.x+. Using the library directly avoids that trap entirely.
- **Passwords are SHA-256'd and base64'd before bcrypt sees them.** bcrypt only
  considers the first 72 bytes and raises on longer input, so two long passwords
  sharing a 72-byte prefix would otherwise collide. The pre-hash is a fixed 44
  bytes, which removes both the crash and the collision.
"""

from __future__ import annotations

import base64
import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
import jwt

from sentinel.config import settings

TokenType = Literal["access", "refresh"]

# NIST SP 800-63B sets 8 as the floor for a user-chosen password. Length is the
# only rule enforced; composition rules push people toward predictable patterns.
MIN_PASSWORD_LENGTH = 8


class InvalidTokenError(Exception):
    """A token was missing, malformed, expired, forged, or of the wrong type."""


def _prepare(password: str) -> bytes:
    """Reduce any password to a fixed 44 bytes bcrypt will always accept."""
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare(password), password_hash.encode("utf-8"))
    except ValueError:
        # A malformed or pre-existing hash is a failed login, never a crash.
        return False


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        subject,
        "access",
        expires_delta or timedelta(minutes=settings.access_token_ttl_minutes),
    )


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return _create_token(
        subject,
        "refresh",
        expires_delta or timedelta(days=settings.refresh_token_ttl_days),
    )


def _decode_token(token: str, expected_type: TokenType) -> str:
    try:
        # Pinning `algorithms` to the one we issue with is what rejects both the
        # alg=none forgery and algorithm-confusion attacks.
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"expected a {expected_type} token")

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise InvalidTokenError("token carries no subject")

    return subject


def decode_access_token(token: str) -> str:
    """Return the subject, or raise InvalidTokenError. Never returns None."""
    return _decode_token(token, "access")


def decode_refresh_token(token: str) -> str:
    """Return the subject, or raise InvalidTokenError. Never returns None."""
    return _decode_token(token, "refresh")
