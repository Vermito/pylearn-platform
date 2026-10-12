import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.module import Module
from app.models.topic import Topic


class TopicRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        module_id: uuid.UUID,
        title: str,
        description: str | None,
        required_tasks_count: int,
        required_test_score: int,
        is_published: bool,
    ) -> Topic | None:
        result = await self.db.execute(
            select(Module)
            .where(
                Module.id == module_id
            )
            .with_for_update()
        )

        module = result.scalar_one_or_none()

        if module is None:
            return None

        max_position = await self.db.scalar(
            select(
                func.coalesce(
                    func.max(Topic.position),
                    0,
                )
            ).where(
                Topic.module_id == module_id
            )
        )

        topic = Topic(
            module_id=module_id,
            title=title,
            description=description,
            position=max_position + 1,
            required_tasks_count=required_tasks_count,
            required_test_score=required_test_score,
            is_published=is_published,
        )

        self.db.add(topic)

        await self.db.commit()
        await self.db.refresh(topic)

        return topic

    async def get_by_id(
        self,
        topic_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> Topic | None:
        query = (
            select(Topic)
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .where(
                Topic.id == topic_id
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_module_id(
        self,
        module_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> list[Topic]:
        query = (
            select(Topic)
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .where(
                Topic.module_id == module_id
            )
            .order_by(
                Topic.position
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        topic: Topic,
        data: dict[str, Any],
    ) -> Topic:
        for field, value in data.items():
            setattr(
                topic,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(topic)

        return topic

    async def delete(
        self,
        topic: Topic,
    ) -> None:
        await self.db.delete(topic)
        await self.db.commit()