from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sentinel.database import async_session
from sentinel.models import User
from sentinel.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from sentinel.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# One message for every login failure, so this endpoint cannot be used to
# discover which email addresses have accounts.
_INVALID_CREDENTIALS = "invalid email or password"
_INVALID_REFRESH = "invalid refresh token"


def _tokens_for(subject: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> TokenResponse:
    email = payload.email.lower()
    async with async_session() as session:
        session.add(User(email=email, password_hash=hash_password(payload.password)))
        try:
            await session.commit()
        except IntegrityError as exc:
            # The unique index is the real guard: two simultaneous registrations
            # for one address both pass a preceding SELECT.
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email already registered",
            ) from exc

    return _tokens_for(email)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    email = payload.email.lower()
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_CREDENTIALS,
        )

    return _tokens_for(email)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    try:
        subject = decode_refresh_token(payload.refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_REFRESH,
        ) from exc

    # A refresh token belonging to a deleted account must stop working.
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.email == subject))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_INVALID_REFRESH,
        )

    return _tokens_for(subject)
