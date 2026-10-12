import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.models.enums import ProgressStatus
from app.schemas.events import (
    TestCompletedEvent,
    TestCompletedPayload,
)
from app.services.test_event import (
    TestEventService,
)


def create_test_event(
    *,
    score: int,
    passed: bool,
    required_tasks_count: int = 3,
    required_test_score: int = 70,
    next_topic_id: uuid.UUID | None = None,
) -> TestCompletedEvent:
    return TestCompletedEvent(
        event_id=uuid.uuid4(),
        event_type="test.completed",
        version=1,
        occurred_at=datetime.now(
            timezone.utc
        ),
        payload=TestCompletedPayload(
            user_id=uuid.uuid4(),
            test_id=uuid.uuid4(),
            topic_id=uuid.uuid4(),
            course_id=uuid.uuid4(),
            next_topic_id=next_topic_id,
            score=score,
            correct_answers=8,
            total_questions=10,
            passed=passed,
            required_tasks_count=(
                required_tasks_count
            ),
            required_test_score=(
                required_test_score
            ),
        ),
    )


@pytest.mark.asyncio
async def test_best_test_score_is_updated():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = TestEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=(
            ProgressStatus
            .IN_PROGRESS.value
        ),
        required_tasks_count=3,
        required_test_score=70,
        solved_tasks_count=2,
        best_test_score=40,
        progress_percent=0,
        completed_at=None,
    )

    repository = SimpleNamespace(
        add_test_result_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_test_completed_once=AsyncMock(
            return_value=True
        ),
        get_or_create_stats=AsyncMock(
            return_value=SimpleNamespace(
                tests_completed=0
            )
        ),
        count_solved_tasks=AsyncMock(
            return_value=2
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    event = create_test_event(
        score=80,
        passed=True,
    )

    await service.process(event)

    assert progress.best_test_score == 80

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_lower_score_does_not_replace_best_score():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = TestEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=(
            ProgressStatus
            .IN_PROGRESS.value
        ),
        required_tasks_count=3,
        required_test_score=70,
        solved_tasks_count=2,
        best_test_score=90,
        progress_percent=0,
        completed_at=None,
    )

    repository = SimpleNamespace(
        add_test_result_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_test_completed_once=AsyncMock(
            return_value=False
        ),
        get_or_create_stats=AsyncMock(),
        count_solved_tasks=AsyncMock(
            return_value=2
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    event = create_test_event(
        score=75,
        passed=True,
    )

    await service.process(event)

    assert progress.best_test_score == 90

    repository.get_or_create_stats.assert_not_awaited()


@pytest.mark.asyncio
async def test_test_can_complete_topic_and_unlock_next():
    db = SimpleNamespace(
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = TestEventService(db)

    progress = SimpleNamespace(
        course_id=None,
        status=(
            ProgressStatus
            .IN_PROGRESS.value
        ),
        required_tasks_count=3,
        required_test_score=70,
        solved_tasks_count=3,
        best_test_score=0,
        progress_percent=50,
        completed_at=None,
    )

    stats = SimpleNamespace(
        tests_completed=0
    )

    repository = SimpleNamespace(
        add_test_result_once=AsyncMock(
            return_value=True
        ),
        get_or_create_progress=AsyncMock(
            return_value=progress
        ),
        mark_test_completed_once=AsyncMock(
            return_value=True
        ),
        get_or_create_stats=AsyncMock(
            return_value=stats
        ),
        count_solved_tasks=AsyncMock(
            return_value=3
        ),
        unlock_topic=AsyncMock(),
    )

    service.repository = repository

    next_topic_id = uuid.uuid4()

    event = create_test_event(
        score=85,
        passed=True,
        next_topic_id=next_topic_id,
    )

    await service.process(event)

    assert progress.best_test_score == 85

    assert (
        progress.status
        == ProgressStatus.COMPLETED.value
    )

    assert progress.progress_percent == 100

    assert progress.completed_at is not None

    assert stats.tests_completed == 1

    repository.unlock_topic.assert_awaited_once_with(
        user_id=event.payload.user_id,
        course_id=event.payload.course_id,
        topic_id=next_topic_id,
    )