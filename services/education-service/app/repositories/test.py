import uuid
from typing import Any

from sqlalchemy import (
    and_,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.answer_option import AnswerOption
from app.models.course import Course
from app.models.module import Module
from app.models.question import Question
from app.models.test import Test
from app.models.topic import Topic


class TestRepository:
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
        description: str | None,
        passing_score: int,
        is_published: bool,
    ) -> Test | None:
        topic = await self.db.get(
            Topic,
            topic_id,
        )

        if topic is None:
            return None

        test = Test(
            topic_id=topic_id,
            title=title,
            description=description,
            passing_score=passing_score,
            is_published=is_published,
        )

        self.db.add(test)

        await self.db.commit()
        await self.db.refresh(test)

        return test

    async def get_by_id(
        self,
        test_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> Test | None:
        query = (
            select(Test)
            .join(
                Topic,
                Test.topic_id == Topic.id,
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
                Test.id == test_id
            )
            .options(
                selectinload(
                    Test.questions
                ).selectinload(
                    Question.options
                )
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Test.is_published.is_(True),
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_topic_id(
        self,
        topic_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> list[Test]:
        query = (
            select(Test)
            .join(
                Topic,
                Test.topic_id == Topic.id,
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
                Test.topic_id == topic_id
            )
            .options(
                selectinload(
                    Test.questions
                ).selectinload(
                    Question.options
                )
            )
            .order_by(
                Test.created_at
            )
        )

        if published_only:
            query = query.where(
                Course.is_published.is_(True),
                Topic.is_published.is_(True),
                Test.is_published.is_(True),
            )

        result = await self.db.execute(query)

        return list(
            result.scalars().unique().all()
        )

    async def update(
        self,
        test: Test,
        data: dict[str, Any],
    ) -> Test:
        for field, value in data.items():
            setattr(
                test,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(test)

        return test

    async def delete(
        self,
        test: Test,
    ) -> None:
        await self.db.delete(test)
        await self.db.commit()

    async def get_question_by_id(
        self,
        question_id: uuid.UUID,
    ) -> Question | None:
        result = await self.db.execute(
            select(Question)
            .where(
                Question.id == question_id
            )
            .options(
                selectinload(
                    Question.options
                )
            )
        )

        return result.scalar_one_or_none()

    async def create_question(
        self,
        *,
        test_id: uuid.UUID,
        question_text: str,
        question_type: str,
        options: list[dict],
    ) -> Question | None:
        result = await self.db.execute(
            select(Test)
            .where(
                Test.id == test_id
            )
            .with_for_update()
        )

        test = result.scalar_one_or_none()

        if test is None:
            return None

        max_position = await self.db.scalar(
            select(
                func.coalesce(
                    func.max(
                        Question.position
                    ),
                    0,
                )
            ).where(
                Question.test_id == test_id
            )
        )

        question = Question(
            test_id=test_id,
            question_text=question_text,
            question_type=question_type,
            position=max_position + 1,
        )

        self.db.add(question)

        await self.db.flush()

        for index, option_data in enumerate(
            options,
            start=1,
        ):
            option = AnswerOption(
                question_id=question.id,
                answer_text=option_data[
                    "answer_text"
                ],
                is_correct=option_data[
                    "is_correct"
                ],
                position=index,
            )

            self.db.add(option)

        await self.db.commit()

        return await self.get_question_by_id(
            question.id
        )

    async def update_question(
        self,
        question: Question,
        *,
        data: dict[str, Any],
        options: list[dict] | None,
    ) -> Question:
        for field, value in data.items():
            setattr(
                question,
                field,
                value,
            )

        if options is not None:
            question.options.clear()

            await self.db.flush()

            for index, option_data in enumerate(
                options,
                start=1,
            ):
                question.options.append(
                    AnswerOption(
                        answer_text=option_data[
                            "answer_text"
                        ],
                        is_correct=option_data[
                            "is_correct"
                        ],
                        position=index,
                    )
                )

        await self.db.commit()

        updated = await self.get_question_by_id(
            question.id
        )

        if updated is None:
            raise RuntimeError(
                "Updated question could not be loaded"
            )

        return updated

    async def delete_question(
        self,
        question: Question,
    ) -> None:
        await self.db.delete(question)
        await self.db.commit()

    async def get_progress_context(
        self,
        test_id: uuid.UUID,
    ) -> dict | None:
        result = await self.db.execute(
            select(
                Topic.id.label(
                    "topic_id"
                ),
                Module.course_id.label(
                    "course_id"
                ),
                Topic.required_tasks_count,
                Topic.required_test_score,
                Topic.position.label(
                    "topic_position"
                ),
                Module.position.label(
                    "module_position"
                ),
            )
            .join(
                Test,
                Test.topic_id == Topic.id,
            )
            .join(
                Module,
                Topic.module_id == Module.id,
            )
            .where(
                Test.id == test_id
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
                Module.course_id
                == row["course_id"],
                Topic.is_published.is_(True),
                or_(
                    Module.position
                    > row["module_position"],
                    and_(
                        Module.position
                        == row[
                            "module_position"
                        ],
                        Topic.position
                        > row[
                            "topic_position"
                        ],
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