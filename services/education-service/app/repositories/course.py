import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    selectinload,
    with_loader_criteria,
)

from app.models.course import Course
from app.models.module import Module
from app.models.topic import Topic


class CourseRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        title: str,
        description: str | None,
        level: str,
        is_published: bool,
    ) -> Course:
        course = Course(
            title=title,
            description=description,
            level=level,
            is_published=is_published,
        )

        self.db.add(course)

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def get_by_id(
        self,
        course_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> Course | None:
        query = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.modules)
                .selectinload(Module.topics)
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True)
            )

            query = query.options(
                with_loader_criteria(
                    Topic,
                    Topic.is_published.is_(True),
                    include_aliases=True,
                )
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        published_only: bool,
        limit: int,
        offset: int,
    ) -> list[Course]:
        query = (
            select(Course)
            .order_by(Course.created_at.desc())
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Course.modules)
                .selectinload(Module.topics)
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True)
            )

            query = query.options(
                with_loader_criteria(
                    Topic,
                    Topic.is_published.is_(True),
                    include_aliases=True,
                )
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        course: Course,
        data: dict[str, Any],
    ) -> Course:
        for field, value in data.items():
            setattr(
                course,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def delete(
        self,
        course: Course,
    ) -> None:
        await self.db.delete(course)
        await self.db.commit()