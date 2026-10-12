import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    TaskDifficulty,
    TaskType,
)


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str = Field(
        min_length=5,
    )

    difficulty: TaskDifficulty

    task_type: TaskType

    starter_code: str | None = None

    entrypoint: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    time_limit_ms: int = Field(
        default=2000,
        ge=100,
        le=5000,
    )

    memory_limit_mb: int = Field(
        default=128,
        ge=32,
        le=256,
    )

    is_published: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    difficulty: TaskDifficulty | None = None

    task_type: TaskType | None = None

    starter_code: str | None = None

    entrypoint: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    time_limit_ms: int | None = Field(
        default=None,
        ge=100,
        le=5000,
    )

    memory_limit_mb: int | None = Field(
        default=None,
        ge=32,
        le=256,
    )

    is_published: bool | None = None


class TestCaseCreate(BaseModel):
    input_data: str | None = None

    expected_output: str = Field(
        min_length=1,
    )

    is_hidden: bool = True


class TestCasePublicResponse(BaseModel):
    id: uuid.UUID
    input_data: str | None
    expected_output: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class TestCaseAdminResponse(
    TestCasePublicResponse
):
    is_hidden: bool


class TaskOptionCreate(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=500,
    )

    is_correct: bool = False


class TaskOptionPublicResponse(BaseModel):
    id: uuid.UUID
    text: str
    position: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskOptionAdminResponse(
    TaskOptionPublicResponse
):
    is_correct: bool


class TaskPublicResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    description: str
    difficulty: TaskDifficulty
    task_type: TaskType
    starter_code: str | None
    entrypoint: str | None
    time_limit_ms: int
    memory_limit_mb: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    test_cases: list[TestCasePublicResponse] = Field(
        default_factory=list
    )

    options: list[TaskOptionPublicResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskAdminResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    description: str
    difficulty: TaskDifficulty
    task_type: TaskType
    starter_code: str | None
    entrypoint: str | None
    time_limit_ms: int
    memory_limit_mb: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    test_cases: list[TestCaseAdminResponse] = Field(
        default_factory=list
    )

    options: list[TaskOptionAdminResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True,
    )