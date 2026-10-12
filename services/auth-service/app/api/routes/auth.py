import uuid

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.database import get_db
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = AuthService(repository)

    return await service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    service = AuthService(repository)

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    return service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        subject = payload.get("sub")

        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = uuid.UUID(subject)

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return {
        "access_token": create_access_token(
            subject=str(user.id),
            role=user.role,
        ),
        "refresh_token": create_refresh_token(
            subject=str(user.id),
            role=user.role,
        ),
        "token_type": "bearer",
    }