import uuid

from pydantic import BaseModel, ConfigDict, Field


class TopicCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    required_tasks_count: int = Field(
        default=0,
        ge=0,
    )

    required_test_score: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    is_published: bool = False


class TopicUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    required_tasks_count: int | None = Field(
        default=None,
        ge=0,
    )

    required_test_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    is_published: bool | None = None


class TopicResponse(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    description: str | None
    position: int
    required_tasks_count: int
    required_test_score: int
    is_published: bool

    model_config = ConfigDict(
        from_attributes=True,
    )