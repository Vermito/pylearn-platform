import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CourseLevel
from app.schemas.module import ModuleResponse


class CourseCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    level: CourseLevel

    is_published: bool = False


class CourseUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    level: CourseLevel | None = None

    is_published: bool | None = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    level: CourseLevel
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class CourseDetailResponse(CourseResponse):
    modules: list[ModuleResponse] = Field(
        default_factory=list,
    )