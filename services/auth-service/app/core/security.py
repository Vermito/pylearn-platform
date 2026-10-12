from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_token(
    subject: str,
    role: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(
    subject: str,
    role: str,
) -> str:
    return create_token(
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )


def create_refresh_token(
    subject: str,
    role: str,
) -> str:
    return create_token(
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.refresh_token_expire_days
        ),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )