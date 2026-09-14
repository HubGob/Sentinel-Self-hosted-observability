from typing import Annotated

from fastapi import Header, HTTPException, status

from sentinel.database import get_db
from sentinel.security import InvalidTokenError, decode_access_token

__all__ = ["get_db", "require_user"]

_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


async def require_user(authorization: Annotated[str | None, Header()] = None) -> str:
    """Return the authenticated subject, or raise 401.

    Everything except the public status page and the health check depends on
    this, so a route added to a gated router is protected by default rather
    than by remembering to add the dependency.
    """
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers=_UNAUTHORIZED_HEADERS,
        )

    token = authorization.split(" ", 1)[1].strip()
    try:
        return decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
            headers=_UNAUTHORIZED_HEADERS,
        ) from exc
