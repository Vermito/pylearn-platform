import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        user_id: uuid.UUID,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "user",
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        self.db.add(user)

        try:
            await self.db.commit()
            await self.db.refresh(user)

        except IntegrityError:
            await self.db.rollback()
            raise

        return user

    async def update_role(
        self,
        user: User,
        role: str,
    ) -> User:
        user.role = role

        try:
            await self.db.commit()
            await self.db.refresh(user)

        except IntegrityError:
            await self.db.rollback()
            raise

        return user