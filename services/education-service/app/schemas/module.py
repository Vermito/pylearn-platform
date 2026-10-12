import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.topic import TopicResponse


class ModuleCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = None


class ModuleUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = None


class ModuleResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: str | None
    position: int

    topics: list[TopicResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True,
    )