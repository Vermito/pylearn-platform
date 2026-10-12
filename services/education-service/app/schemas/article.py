import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse


class ArticleCreate(BaseModel):
    category_id: uuid.UUID

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    content: str = Field(
        min_length=10,
    )

    is_published: bool = False


class ArticleUpdate(BaseModel):
    category_id: uuid.UUID | None = None

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    content: str | None = Field(
        default=None,
        min_length=10,
    )

    is_published: bool | None = None


class ArticleResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    slug: str
    content: str
    is_published: bool
    created_at: datetime
    updated_at: datetime

    category: CategoryResponse

    model_config = ConfigDict(
        from_attributes=True,
    )