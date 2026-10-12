import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        name: str,
        slug: str,
    ) -> Category:
        category = Category(
            name=name,
            slug=slug,
        )

        self.db.add(category)

        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def get_by_id(
        self,
        category_id: uuid.UUID,
    ) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.slug == slug
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[Category]:
        result = await self.db.execute(
            select(Category).order_by(
                Category.name
            )
        )

        return list(
            result.scalars().all()
        )