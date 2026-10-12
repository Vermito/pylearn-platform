import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TaskSubmissionPayload(BaseModel):
    user_id: uuid.UUID

    task_id: uuid.UUID
    topic_id: uuid.UUID
    course_id: uuid.UUID

    next_topic_id: uuid.UUID | None = None

    code: str

    status: Literal[
        "success",
        "failed",
        "error",
        "timeout",
    ]

    passed_tests: int
    total_tests: int

    execution_time_ms: float

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ]

    required_tasks_count: int
    required_test_score: int


class TaskSubmissionEvaluatedEvent(BaseModel):
    event_id: uuid.UUID

    event_type: Literal[
        "task_submission_evaluated"
    ]

    version: Literal[2]

    occurred_at: datetime

    payload: TaskSubmissionPayload


class TestCompletedPayload(BaseModel):
    user_id: uuid.UUID

    test_id: uuid.UUID
    topic_id: uuid.UUID
    course_id: uuid.UUID

    next_topic_id: uuid.UUID | None = None

    score: int

    correct_answers: int
    total_questions: int

    passed: bool

    required_tasks_count: int
    required_test_score: int


class TestCompletedEvent(BaseModel):
    event_id: uuid.UUID

    event_type: Literal[
        "test.completed"
    ]

    version: Literal[1]

    occurred_at: datetime

    payload: TestCompletedPayload