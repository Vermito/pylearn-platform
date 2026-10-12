import uuid

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = ConfigDict(
        from_attributes=True,
    )