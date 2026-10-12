import uuid
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    selectinload,
    with_loader_criteria,
)

from app.models.course import Course
from app.models.module import Module
from app.models.task import Task
from app.models.task_option import TaskOption
from app.models.test_case import TestCase
from app.models.topic import Topic


class TaskRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        topic_id: uuid.UUID,
        title: str,
        description: str,
        difficulty: str,
        task_type: str,
        starter_code: str | None,
        entrypoint: str | None,
        time_limit_ms: int,
        memory_limit_mb: int,
        is_published: bool,
    ) -> Task | None:
        topic = await self.db.get(
            Topic,
            topic_id,
        )

        if topic is None:
            return None

        task = Task(
            topic_id=topic_id,
            title=title,
            description=description,
            difficulty=difficulty,
            task_type=task_type,
            starter_code=starter_code,
            entrypoint=entrypoint,
            time_limit_ms=time_limit_ms,
            memory_limit_mb=memory_limit_mb,
            is_published=is_published,
        )

        self.db.add(task)

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def get_by_id(
        self,
        task_id: uuid.UUID,
        *,
        published_only: bool,
        include_hidden: bool,
    ) -> Task | None:
        query = (
            select(Task)
            .join(
                Topic,
                Task.topic_id == Topic.id,
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
                Task.id == task_id
            )
            .options(
                selectinload(Task.test_cases),
                selectinload(Task.options),
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Task.is_published.is_(True),
            )

        if not include_hidden:
            query = query.options(
                with_loader_criteria(
                    TestCase,
                    TestCase.is_hidden.is_(False),
                    include_aliases=True,
                )
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_topic_id(
        self,
        topic_id: uuid.UUID,
        *,
        published_only: bool,
        include_hidden: bool,
        difficulty: str | None,
        task_type: str | None,
    ) -> list[Task]:
        query = (
            select(Task)
            .join(
                Topic,
                Task.topic_id == Topic.id,
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
                Task.topic_id == topic_id
            )
            .options(
                selectinload(Task.test_cases),
                selectinload(Task.options),
            )
            .order_by(
                Task.created_at
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Task.is_published.is_(True),
            )

        if not include_hidden:
            query = query.options(
                with_loader_criteria(
                    TestCase,
                    TestCase.is_hidden.is_(False),
                    include_aliases=True,
                )
            )

        if difficulty is not None:
            query = query.where(
                Task.difficulty == difficulty
            )

        if task_type is not None:
            query = query.where(
                Task.task_type == task_type
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        task: Task,
        data: dict[str, Any],
    ) -> Task:
        for field, value in data.items():
            setattr(
                task,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def delete(
        self,
        task: Task,
    ) -> None:
        await self.db.delete(task)
        await self.db.commit()

    async def create_test_case(
        self,
        *,
        task_id: uuid.UUID,
        input_data: str | None,
        expected_output: str,
        is_hidden: bool,
    ) -> TestCase:
        test_case = TestCase(
            task_id=task_id,
            input_data=input_data,
            expected_output=expected_output,
            is_hidden=is_hidden,
        )

        self.db.add(test_case)

        await self.db.commit()
        await self.db.refresh(test_case)

        return test_case

    async def create_option(
        self,
        *,
        task_id: uuid.UUID,
        text: str,
        is_correct: bool,
    ) -> TaskOption | None:
        result = await self.db.execute(
            select(Task)
            .where(
                Task.id == task_id
            )
            .with_for_update()
        )

        task = result.scalar_one_or_none()

        if task is None:
            return None

        max_position = await self.db.scalar(
            select(
                func.coalesce(
                    func.max(TaskOption.position),
                    0,
                )
            ).where(
                TaskOption.task_id == task_id
            )
        )

        option = TaskOption(
            task_id=task_id,
            text=text,
            is_correct=is_correct,
            position=max_position + 1,
        )

        self.db.add(option)

        await self.db.commit()
        await self.db.refresh(option)

        return option

    async def get_progress_context(
        self,
        task_id: uuid.UUID,
    ) -> dict | None:
        result = await self.db.execute(
            select(
                Topic.id.label("topic_id"),
                Module.course_id.label("course_id"),
                Topic.required_tasks_count,
                Topic.required_test_score,
                Topic.position.label("topic_position"),
                Module.position.label("module_position"),
            )
            .join(
                Task,
                Task.topic_id == Topic.id,
            )
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .where(
                Task.id == task_id
            )
        )

        row = result.mappings().one_or_none()

        if row is None:
            return None

        next_topic_result = await self.db.execute(
            select(Topic.id)
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .where(
                Module.course_id == row["course_id"],
                Topic.is_published.is_(True),
                or_(
                    Module.position
                    > row["module_position"],

                    and_(
                        Module.position
                        == row["module_position"],

                        Topic.position
                        > row["topic_position"],
                    ),
                ),
            )
            .order_by(
                Module.position.asc(),
                Topic.position.asc(),
            )
            .limit(1)
        )

        next_topic_id = (
            next_topic_result.scalar_one_or_none()
        )

        return {
            "course_id": row["course_id"],
            "topic_id": row["topic_id"],
            "required_tasks_count": (
                row["required_tasks_count"]
            ),
            "required_test_score": (
                row["required_test_score"]
            ),
            "next_topic_id": next_topic_id,
        }