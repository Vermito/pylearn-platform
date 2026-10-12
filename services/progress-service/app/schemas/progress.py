import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserStatsResponse(BaseModel):
    user_id: uuid.UUID

    xp: int
    tasks_solved: int
    tests_completed: int

    current_streak: int
    longest_streak: int

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskSubmissionResponse(BaseModel):
    id: uuid.UUID

    task_id: uuid.UUID

    code: str

    status: str

    passed_tests: int
    total_tests: int

    execution_time_ms: float

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SolvedTaskResponse(BaseModel):
    task_id: uuid.UUID
    first_solved_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class LeaderboardEntry(BaseModel):
    position: int

    user_id: uuid.UUID

    xp: int
    tasks_solved: int
    current_streak: int


class UserProgressResponse(BaseModel):
    course_id: uuid.UUID
    topic_id: uuid.UUID

    status: str

    progress_percent: int

    solved_tasks_count: int
    required_tasks_count: int

    best_test_score: int
    required_test_score: int

    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )