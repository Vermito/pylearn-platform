import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.models.enums import ProgressStatus
from app.schemas.events import (
    TaskSubmissionEvaluatedEvent,
    TaskSubmissionPayload,
)
from app.services.submission_event import (
    SubmissionEventService,
)


def create_event(
    *,
    task_status: str = "success",
    difficulty: str = "easy",
    required_tasks_count: int = 3,
    required_test_score: int = 70,
    next_topic_id: uuid.UUID | None = None,
) -> TaskSubmissionEvaluatedEvent:
    return TaskSubmissionEvaluatedEvent(
        event_id=uuid.uuid4(),
        event_type="task_submission_evaluated",
        version=2,
        occurred_at=datetime.now(
            timezone.utc
        ),
        payload=TaskSubmissionPayload(
            user_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            topic_id=uuid.uuid4(),
            course_id=uuid.uuid4(),
            next_topic_id=next_topic_id,
            code=(
                "def square(n):\n"
                "    return n * n"
            ),
            status=task_status,
            passed_tests=3,
            total_tests=3,
            execution_time_ms=125.5,
            difficulty=difficulty,
            required_tasks_count=(
                required_tasks_count
            ),
            required_test_score=(
                required_test_score
            ),
        ),
    )


@pytest.mark.asyncio
async def test_duplicate_event_is_not_processed_twice():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = SubmissionEventService(db)

    repository = SimpleNamespace(
        add_submission_once=AsyncMock(
            return_value=False
        ),
    )

    service.repository = repository

    event = create_event()

    await service.process(event)

    repository.add_submission_once.assert_awaited_once()

    db.rollback.assert_awaited_once()
    db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_first_easy_task_awards_10_xp():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = SubmissionEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=ProgressStatus.AVAILABLE.value,
        required_tasks_count=0,
        required_test_score=0,
        solved_tasks_count=0,
        best_test_score=0,
        progress_percent=0,
        completed_at=None,
    )

    stats = SimpleNamespace(
        xp=0,
        tasks_solved=0,
    )

    repository = SimpleNamespace(
        add_submission_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_solved_once=AsyncMock(
            return_value=True
        ),
        get_or_create_stats=AsyncMock(
            return_value=stats
        ),
        count_solved_tasks=AsyncMock(
            return_value=1
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    event = create_event(
        difficulty="easy",
        required_tasks_count=3,
        required_test_score=70,
    )

    await service.process(event)

    assert stats.xp == 10
    assert stats.tasks_solved == 1

    assert (
        progress.status
        == ProgressStatus.IN_PROGRESS.value
    )

    assert progress.solved_tasks_count == 1
    assert progress.progress_percent == 17

    repository.unlock_topic.assert_not_awaited()

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_completed_topic_unlocks_next_topic():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = SubmissionEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=(
            ProgressStatus
            .IN_PROGRESS.value
        ),
        required_tasks_count=0,
        required_test_score=0,
        solved_tasks_count=0,
        best_test_score=0,
        progress_percent=0,
        completed_at=None,
    )

    stats = SimpleNamespace(
        xp=0,
        tasks_solved=0,
    )

    repository = SimpleNamespace(
        add_submission_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_solved_once=AsyncMock(
            return_value=True
        ),
        get_or_create_stats=AsyncMock(
            return_value=stats
        ),
        count_solved_tasks=AsyncMock(
            return_value=1
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    next_topic_id = uuid.uuid4()

    event = create_event(
        difficulty="easy",
        required_tasks_count=1,
        required_test_score=0,
        next_topic_id=next_topic_id,
    )

    await service.process(event)

    assert (
        progress.status
        == ProgressStatus.COMPLETED.value
    )

    assert progress.progress_percent == 100

    assert progress.completed_at is not None

    repository.unlock_topic.assert_awaited_once_with(
        user_id=event.payload.user_id,
        course_id=event.payload.course_id,
        topic_id=next_topic_id,
    )

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_repeated_success_does_not_award_xp_again():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = SubmissionEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=(
            ProgressStatus
            .IN_PROGRESS.value
        ),
        required_tasks_count=0,
        required_test_score=0,
        solved_tasks_count=1,
        best_test_score=0,
        progress_percent=0,
        completed_at=None,
    )

    repository = SimpleNamespace(
        add_submission_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_solved_once=AsyncMock(
            return_value=False
        ),
        get_or_create_stats=AsyncMock(),
        count_solved_tasks=AsyncMock(
            return_value=1
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    event = create_event(
        required_tasks_count=3,
        required_test_score=70,
    )

    await service.process(event)

    repository.get_or_create_stats.assert_not_awaited()

    db.commit.assert_awaited_once()