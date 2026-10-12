import uuid

from fastapi import HTTPException, status
from slugify import slugify

from app.api.dependencies import CurrentUser
from app.models.article import Article
from app.repositories.article import ArticleRepository
from app.repositories.category import CategoryRepository
from app.repositories.topic import TopicRepository
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
)


class ArticleService:
    def __init__(
        self,
        article_repository: ArticleRepository,
        category_repository: CategoryRepository,
        topic_repository: TopicRepository,
    ):
        self.article_repository = article_repository
        self.category_repository = category_repository
        self.topic_repository = topic_repository

    async def create(
        self,
        topic_id: uuid.UUID,
        data: ArticleCreate,
    ) -> Article:
        topic = await self.topic_repository.get_by_id(
            topic_id,
            published_only=False,
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        category = (
            await self.category_repository.get_by_id(
                data.category_id
            )
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        base_slug = slugify(data.title)
        slug = base_slug
        counter = 2

        while (
            await self.article_repository.get_by_slug(
                slug,
                published_only=False,
            )
            is not None
        ):
            slug = f"{base_slug}-{counter}"
            counter += 1

        article = await self.article_repository.create(
            topic_id=topic_id,
            category_id=data.category_id,
            title=data.title,
            slug=slug,
            content=data.content,
            is_published=data.is_published,
        )

        created_article = (
            await self.article_repository.get_by_id(
                article.id
            )
        )

        if created_article is None:
            raise HTTPException(
                status_code=500,
                detail="Created article could not be loaded",
            )

        return created_article

    async def get_all(
        self,
        current_user: CurrentUser,
        category: str | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[Article]:
        return await self.article_repository.get_all(
            published_only=(
                current_user.role != "admin"
            ),
            category_slug=category,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_by_slug(
        self,
        slug: str,
        current_user: CurrentUser,
    ) -> Article:
        article = (
            await self.article_repository.get_by_slug(
                slug,
                published_only=(
                    current_user.role != "admin"
                ),
            )
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found",
            )

        return article

    async def update(
        self,
        article_id: uuid.UUID,
        data: ArticleUpdate,
    ) -> Article:
        article = (
            await self.article_repository.get_by_id(
                article_id
            )
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "category_id" in update_data:
            category = (
                await self.category_repository.get_by_id(
                    update_data["category_id"]
                )
            )

            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found",
                )

        if "title" in update_data:
            base_slug = slugify(
                update_data["title"]
            )

            new_slug = base_slug
            counter = 2

            while True:
                existing = (
                    await self.article_repository.get_by_slug(
                        new_slug,
                        published_only=False,
                    )
                )

                if (
                    existing is None
                    or existing.id == article.id
                ):
                    break

                new_slug = (
                    f"{base_slug}-{counter}"
                )
                counter += 1

            update_data["slug"] = new_slug

        await self.article_repository.update(
            article,
            update_data,
        )

        updated_article = (
            await self.article_repository.get_by_id(
                article_id
            )
        )

        if updated_article is None:
            raise HTTPException(
                status_code=500,
                detail="Updated article could not be loaded",
            )

        return updated_article

    async def delete(
        self,
        article_id: uuid.UUID,
    ) -> None:
        article = (
            await self.article_repository.get_by_id(
                article_id
            )
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found",
            )

        await self.article_repository.delete(
            article
        )