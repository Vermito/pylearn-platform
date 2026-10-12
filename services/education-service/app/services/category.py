from fastapi import HTTPException, status
from slugify import slugify

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository,
    ):
        self.repository = repository

    async def create(
        self,
        data: CategoryCreate,
    ) -> Category:
        slug = slugify(data.name)

        existing = await self.repository.get_by_slug(
            slug
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists",
            )

        return await self.repository.create(
            name=data.name,
            slug=slug,
        )

    async def get_all(
        self,
    ) -> list[Category]:
        return await self.repository.get_all()