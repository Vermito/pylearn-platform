import uuid

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.enums import MaterialType


class MaterialCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    material_type: MaterialType

    url: AnyHttpUrl


class MaterialUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    material_type: MaterialType | None = None

    url: AnyHttpUrl | None = None


class MaterialResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    description: str | None
    material_type: MaterialType
    url: str

    model_config = ConfigDict(
        from_attributes=True,
    )