"""Tests for password hashing and JWT issuing/verification.

Each "rejects" test below maps to a real, well-known vulnerability:
- token signed with another secret -> signature forgery
- expired token                    -> replay of stale credentials
- access token used as a refresh   -> type confusion
- alg=none token                   -> the classic unsecured-JWT forgery
"""

import base64
import json
from datetime import timedelta

import jwt
import pytest

from sentinel import security
from sentinel.config import INSECURE_DEFAULT_SECRET, MINIMUM_SECRET_BYTES
from sentinel.security import InvalidTokenError


def test_hash_password_does_not_return_the_plaintext() -> None:
    assert security.hash_password("correct horse") != "correct horse"


def test_verify_password_accepts_the_right_password() -> None:
    hashed = security.hash_password("correct horse")
    assert security.verify_password("correct horse", hashed) is True


def test_verify_password_rejects_the_wrong_password() -> None:
    hashed = security.hash_password("correct horse")
    assert security.verify_password("battery staple", hashed) is False


def test_verify_password_rejects_a_malformed_hash() -> None:
    assert security.verify_password("anything", "not-a-bcrypt-hash") is False


def test_same_password_hashes_differently() -> None:
    assert security.hash_password("same") != security.hash_password("same")


def test_long_passwords_do_not_crash() -> None:
    # bcrypt raises on inputs over 72 bytes, so this must be handled, not hoped for.
    password = "a" * 200
    hashed = security.hash_password(password)
    assert security.verify_password(password, hashed) is True


def test_access_token_roundtrips_to_its_subject() -> None:
    token = security.create_access_token("user@example.com")
    assert security.decode_access_token(token) == "user@example.com"


def test_refresh_token_roundtrips_to_its_subject() -> None:
    token = security.create_refresh_token("user@example.com")
    assert security.decode_refresh_token(token) == "user@example.com"


def test_token_signed_with_another_secret_is_rejected() -> None:
    forged = jwt.encode(
        {"sub": "attacker@example.com", "type": "access"},
        "a-different-secret",
        algorithm="HS256",
    )
    with pytest.raises(InvalidTokenError):
        security.decode_access_token(forged)


def test_expired_access_token_is_rejected() -> None:
    token = security.create_access_token("user@example.com", expires_delta=timedelta(seconds=-1))
    with pytest.raises(InvalidTokenError):
        security.decode_access_token(token)


def test_access_token_cannot_be_used_as_a_refresh_token() -> None:
    token = security.create_access_token("user@example.com")
    with pytest.raises(InvalidTokenError):
        security.decode_refresh_token(token)


def test_refresh_token_cannot_be_used_as_an_access_token() -> None:
    token = security.create_refresh_token("user@example.com")
    with pytest.raises(InvalidTokenError):
        security.decode_access_token(token)


def test_alg_none_forgery_is_rejected() -> None:
    def segment(payload: dict[str, str]) -> str:
        raw = json.dumps(payload, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    header = segment({"alg": "none", "typ": "JWT"})
    body = segment({"sub": "attacker@example.com", "type": "access"})
    forged = f"{header}.{body}."
    with pytest.raises(InvalidTokenError):
        security.decode_access_token(forged)


@pytest.mark.parametrize("garbage", ["", "not.a.token", "a.b.c"])
def test_garbage_tokens_are_rejected(garbage: str) -> None:
    with pytest.raises(InvalidTokenError):
        security.decode_access_token(garbage)


def test_the_development_default_secret_meets_the_hmac_minimum() -> None:
    # PyJWT warns below 32 bytes; shipping a default that trips its own warning
    # would train people to ignore it.
    assert len(INSECURE_DEFAULT_SECRET.encode("utf-8")) >= MINIMUM_SECRET_BYTES
