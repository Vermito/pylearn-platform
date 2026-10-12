from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ProgressStatus
from app.repositories.progress import (
    ProgressRepository,
)
from app.schemas.events import (
    TaskSubmissionEvaluatedEvent,
)
from app.services.progress_calculator import (
    calculate_progress_percent,
    is_topic_completed,
)


XP_REWARDS = {
    "easy": 10,
    "medium": 20,
    "hard": 30,
}


class SubmissionEventService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.repository = (
            ProgressRepository(db)
        )

    async def process(
        self,
        event: TaskSubmissionEvaluatedEvent,
    ) -> None:
        payload = event.payload

        inserted = (
            await self.repository.add_submission_once(
                event_id=event.event_id,
                user_id=payload.user_id,
                task_id=payload.task_id,
                course_id=payload.course_id,
                topic_id=payload.topic_id,
                code=payload.code,
                status=payload.status,
                passed_tests=(
                    payload.passed_tests
                ),
                total_tests=(
                    payload.total_tests
                ),
                execution_time_ms=(
                    payload.execution_time_ms
                ),
            )
        )

        if not inserted:
            await self.db.rollback()
            return

        progress = (
            await self.repository
            .get_or_create_progress(
                user_id=payload.user_id,
                course_id=payload.course_id,
                topic_id=payload.topic_id,
            )
        )

        progress.course_id = (
            payload.course_id
        )

        progress.required_tasks_count = (
            payload.required_tasks_count
        )

        progress.required_test_score = (
            payload.required_test_score
        )

        if (
            progress.status
            == ProgressStatus.AVAILABLE.value
        ):
            progress.status = (
                ProgressStatus.IN_PROGRESS.value
            )

        if payload.status == "success":
            first_solve = (
                await self.repository
                .mark_solved_once(
                    user_id=payload.user_id,
                    task_id=payload.task_id,
                    course_id=payload.course_id,
                    topic_id=payload.topic_id,
                )
            )

            if first_solve:
                stats = (
                    await self.repository
                    .get_or_create_stats(
                        payload.user_id
                    )
                )

                reward = XP_REWARDS[
                    payload.difficulty
                ]

                stats.xp += reward
                stats.tasks_solved += 1

        solved_tasks_count = (
            await self.repository
            .count_solved_tasks(
                user_id=payload.user_id,
                topic_id=payload.topic_id,
            )
        )

        progress.solved_tasks_count = (
            solved_tasks_count
        )

        progress.progress_percent = (
            calculate_progress_percent(
                solved_tasks=(
                    solved_tasks_count
                ),
                required_tasks=(
                    payload
                    .required_tasks_count
                ),
                best_test_score=(
                    progress.best_test_score
                ),
                required_test_score=(
                    payload
                    .required_test_score
                ),
            )
        )

        completed = is_topic_completed(
            solved_tasks=solved_tasks_count,
            required_tasks=(
                payload.required_tasks_count
            ),
            best_test_score=(
                progress.best_test_score
            ),
            required_test_score=(
                payload.required_test_score
            ),
        )

        if (
            completed
            and progress.status
            != ProgressStatus.COMPLETED.value
        ):
            progress.status = (
                ProgressStatus.COMPLETED.value
            )

            progress.progress_percent = 100

            progress.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

            if (
                payload.next_topic_id
                is not None
            ):
                await (
                    self.repository.unlock_topic(
                        user_id=(
                            payload.user_id
                        ),
                        course_id=(
                            payload.course_id
                        ),
                        topic_id=(
                            payload.next_topic_id
                        ),
                    )
                )

        await self.db.commit()