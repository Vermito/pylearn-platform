import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from app.models.course import Course
from app.models.module import Module
from app.models.topic import Topic


class ModuleRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        course_id: uuid.UUID,
        title: str,
        description: str | None,
    ) -> Module | None:
        # Блокируем строку курса на время создания модуля.
        # Это уменьшает вероятность, что два параллельных
        # запроса получат одну position.
        result = await self.db.execute(
            select(Course)
            .where(Course.id == course_id)
            .with_for_update()
        )

        course = result.scalar_one_or_none()

        if course is None:
            return None

        max_position = await self.db.scalar(
            select(
                func.coalesce(
                    func.max(Module.position),
                    0,
                )
            ).where(
                Module.course_id == course_id
            )
        )

        module = Module(
            course_id=course_id,
            title=title,
            description=description,
            position=max_position + 1,
        )

        self.db.add(module)

        await self.db.commit()
        await self.db.refresh(module)

        return module

    async def get_by_id(
        self,
        module_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> Module | None:
        query = (
            select(Module)
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .where(
                Module.id == module_id
            )
            .options(
                selectinload(Module.topics)
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

    async def get_by_course_id(
        self,
        course_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> list[Module]:
        query = (
            select(Module)
            .join(
                Course,
                Module.course_id == Course.id,
            )
            .where(
                Module.course_id == course_id
            )
            .order_by(
                Module.position
            )
            .options(
                selectinload(Module.topics)
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
        module: Module,
        data: dict[str, Any],
    ) -> Module:
        for field, value in data.items():
            setattr(
                module,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(module)

        return module

    async def delete(
        self,
        module: Module,
    ) -> None:
        await self.db.delete(module)
        await self.db.commit()