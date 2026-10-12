import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.models.category import Category
from app.models.course import Course
from app.models.module import Module
from app.models.topic import Topic


class ArticleRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        topic_id: uuid.UUID,
        category_id: uuid.UUID,
        title: str,
        slug: str,
        content: str,
        is_published: bool,
    ) -> Article:
        article = Article(
            topic_id=topic_id,
            category_id=category_id,
            title=title,
            slug=slug,
            content=content,
            is_published=is_published,
        )

        self.db.add(article)

        await self.db.commit()
        await self.db.refresh(article)

        return article

    async def get_by_slug(
        self,
        slug: str,
        *,
        published_only: bool,
    ) -> Article | None:
        query = (
            select(Article)
            .join(
                Topic,
                Article.topic_id == Topic.id,
            )
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .where(
                Article.slug == slug
            )
            .options(
                selectinload(Article.category)
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Article.is_published.is_(True),
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        article_id: uuid.UUID,
    ) -> Article | None:
        result = await self.db.execute(
            select(Article)
            .where(
                Article.id == article_id
            )
            .options(
                selectinload(Article.category)
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        published_only: bool,
        category_slug: str | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[Article]:
        query = (
            select(Article)
            .join(
                Category,
                Article.category_id == Category.id,
            )
            .join(
                Topic,
                Article.topic_id == Topic.id,
            )
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .options(
                selectinload(Article.category)
            )
            .order_by(
                Article.created_at.desc()
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Article.is_published.is_(True),
            )

        if category_slug is not None:
            query = query.where(
                Category.slug == category_slug
            )

        if search is not None:
            search_value = f"%{search}%"

            query = query.where(
                or_(
                    Article.title.ilike(search_value),
                    Article.content.ilike(search_value),
                )
            )

        query = (
            query
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        article: Article,
        data: dict[str, Any],
    ) -> Article:
        for field, value in data.items():
            setattr(
                article,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(article)

        return article

    async def delete(
        self,
        article: Article,
    ) -> None:
        await self.db.delete(article)
        await self.db.commit()