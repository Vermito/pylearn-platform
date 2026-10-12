import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completed_test import CompletedTest
from app.models.enums import ProgressStatus
from app.models.solved_task import SolvedTask
from app.models.task_submission import TaskSubmission
from app.models.test_result import TestResult
from app.models.user_progress import UserProgress
from app.models.user_stats import UserStats


class ProgressRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def add_submission_once(
        self,
        *,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        course_id: uuid.UUID,
        topic_id: uuid.UUID,
        code: str,
        status: str,
        passed_tests: int,
        total_tests: int,
        execution_time_ms: float,
    ) -> bool:
        statement = (
            insert(TaskSubmission)
            .values(
                event_id=event_id,
                user_id=user_id,
                task_id=task_id,
                course_id=course_id,
                topic_id=topic_id,
                code=code,
                status=status,
                passed_tests=passed_tests,
                total_tests=total_tests,
                execution_time_ms=(
                    execution_time_ms
                ),
            )
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
            .returning(
                TaskSubmission.id
            )
        )

        result = await self.db.execute(
            statement
        )

        return (
            result.scalar_one_or_none()
            is not None
        )

    async def add_test_result_once(
        self,
        *,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        test_id: uuid.UUID,
        course_id: uuid.UUID,
        topic_id: uuid.UUID,
        score: int,
        correct_answers: int,
        total_questions: int,
        passed: bool,
    ) -> bool:
        statement = (
            insert(TestResult)
            .values(
                event_id=event_id,
                user_id=user_id,
                test_id=test_id,
                course_id=course_id,
                topic_id=topic_id,
                score=score,
                correct_answers=(
                    correct_answers
                ),
                total_questions=(
                    total_questions
                ),
                passed=passed,
            )
            .on_conflict_do_nothing(
                index_elements=["event_id"]
            )
            .returning(
                TestResult.id
            )
        )

        result = await self.db.execute(
            statement
        )

        return (
            result.scalar_one_or_none()
            is not None
        )

    async def get_or_create_stats(
        self,
        user_id: uuid.UUID,
    ) -> UserStats:
        statement = (
            insert(UserStats)
            .values(
                user_id=user_id,
                xp=0,
                tasks_solved=0,
                tests_completed=0,
                current_streak=0,
                longest_streak=0,
            )
            .on_conflict_do_nothing(
                index_elements=["user_id"]
            )
        )

        await self.db.execute(statement)

        result = await self.db.execute(
            select(UserStats).where(
                UserStats.user_id == user_id
            )
        )

        return result.scalar_one()

    async def mark_solved_once(
        self,
        *,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        course_id: uuid.UUID,
        topic_id: uuid.UUID,
    ) -> bool:
        statement = (
            insert(SolvedTask)
            .values(
                user_id=user_id,
                task_id=task_id,
                course_id=course_id,
                topic_id=topic_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "user_id",
                    "task_id",
                ]
            )
            .returning(
                SolvedTask.id
            )
        )

        result = await self.db.execute(
            statement
        )

        return (
            result.scalar_one_or_none()
            is not None
        )

    async def mark_test_completed_once(
        self,
        *,
        user_id: uuid.UUID,
        test_id: uuid.UUID,
    ) -> bool:
        statement = (
            insert(CompletedTest)
            .values(
                user_id=user_id,
                test_id=test_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "user_id",
                    "test_id",
                ]
            )
            .returning(
                CompletedTest.id
            )
        )

        result = await self.db.execute(
            statement
        )

        return (
            result.scalar_one_or_none()
            is not None
        )

    async def count_solved_tasks(
        self,
        *,
        user_id: uuid.UUID,
        topic_id: uuid.UUID,
    ) -> int:
        result = await self.db.execute(
            select(
                func.count(
                    SolvedTask.id
                )
            ).where(
                SolvedTask.user_id
                == user_id,
                SolvedTask.topic_id
                == topic_id,
            )
        )

        return result.scalar_one()

    async def get_or_create_progress(
        self,
        *,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        topic_id: uuid.UUID,
    ) -> UserProgress:
        statement = (
            insert(UserProgress)
            .values(
                user_id=user_id,
                course_id=course_id,
                topic_id=topic_id,
                status=(
                    ProgressStatus
                    .IN_PROGRESS.value
                ),
                progress_percent=0,
                solved_tasks_count=0,
                required_tasks_count=0,
                best_test_score=0,
                required_test_score=0,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "user_id",
                    "topic_id",
                ]
            )
        )

        await self.db.execute(statement)

        result = await self.db.execute(
            select(UserProgress)
            .where(
                UserProgress.user_id
                == user_id,
                UserProgress.topic_id
                == topic_id,
            )
            .with_for_update()
        )

        return result.scalar_one()

    async def unlock_topic(
        self,
        *,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        topic_id: uuid.UUID,
    ) -> None:
        statement = (
            insert(UserProgress)
            .values(
                user_id=user_id,
                course_id=course_id,
                topic_id=topic_id,
                status=(
                    ProgressStatus
                    .AVAILABLE.value
                ),
                progress_percent=0,
                solved_tasks_count=0,
                required_tasks_count=0,
                best_test_score=0,
                required_test_score=0,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    "user_id",
                    "topic_id",
                ]
            )
        )

        await self.db.execute(statement)

        result = await self.db.execute(
            select(UserProgress)
            .where(
                UserProgress.user_id
                == user_id,
                UserProgress.topic_id
                == topic_id,
            )
            .with_for_update()
        )

        progress = result.scalar_one()

        if (
            progress.status
            == ProgressStatus.LOCKED.value
        ):
            progress.status = (
                ProgressStatus.AVAILABLE.value
            )

    async def get_stats(
        self,
        user_id: uuid.UUID,
    ) -> UserStats | None:
        result = await self.db.execute(
            select(UserStats).where(
                UserStats.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_submissions(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[TaskSubmission]:
        result = await self.db.execute(
            select(TaskSubmission)
            .where(
                TaskSubmission.user_id
                == user_id
            )
            .order_by(
                TaskSubmission
                .created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_solved_tasks(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[SolvedTask]:
        result = await self.db.execute(
            select(SolvedTask)
            .where(
                SolvedTask.user_id
                == user_id
            )
            .order_by(
                SolvedTask
                .first_solved_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_leaderboard(
        self,
        *,
        limit: int,
    ) -> list[UserStats]:
        result = await self.db.execute(
            select(UserStats)
            .order_by(
                UserStats.xp.desc(),
                UserStats.tasks_solved.desc(),
            )
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_user_progress(
        self,
        user_id: uuid.UUID,
        *,
        course_id: uuid.UUID | None = None,
    ) -> list[UserProgress]:
        query = (
            select(UserProgress)
            .where(
                UserProgress.user_id
                == user_id
            )
            .order_by(
                UserProgress.started_at
            )
        )

        if course_id is not None:
            query = query.where(
                UserProgress.course_id
                == course_id
            )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )