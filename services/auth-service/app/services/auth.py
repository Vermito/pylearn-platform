from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    async def register(
        self,
        data: UserCreate,
    ) -> User:
        existing_email = await self.user_repository.get_by_email(
            data.email
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        existing_username = (
            await self.user_repository.get_by_username(
                data.username
            )
        )

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        hashed_password = hash_password(data.password)

        try:
            return await self.user_repository.create(
                username=data.username,
                email=data.email,
                password_hash=hashed_password,
            )

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User:
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        return user

    @staticmethod
    def create_tokens(user: User) -> dict[str, str]:
        subject = str(user.id)

        return {
            "access_token": create_access_token(
                subject=subject,
                role=user.role,
            ),
            "refresh_token": create_refresh_token(
                subject=subject,
                role=user.role,
            ),
            "token_type": "bearer",
        }