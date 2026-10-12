import uuid

from fastapi import HTTPException, status

from app.models.material import Material
from app.repositories.material import MaterialRepository
from app.repositories.topic import TopicRepository
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
)


class MaterialService:
    def __init__(
        self,
        material_repository: MaterialRepository,
        topic_repository: TopicRepository,
    ):
        self.material_repository = material_repository
        self.topic_repository = topic_repository

    async def create(
        self,
        topic_id: uuid.UUID,
        data: MaterialCreate,
    ) -> Material:
        topic = await self.topic_repository.get_by_id(
            topic_id,
            published_only=False,
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        return await self.material_repository.create(
            topic_id=topic_id,
            title=data.title,
            description=data.description,
            material_type=data.material_type.value,
            url=str(data.url),
        )

    async def get_by_topic(
        self,
        topic_id: uuid.UUID,
    ) -> list[Material]:
        return await self.material_repository.get_by_topic_id(
            topic_id
        )

    async def update(
        self,
        material_id: uuid.UUID,
        data: MaterialUpdate,
    ) -> Material:
        material = (
            await self.material_repository.get_by_id(
                material_id
            )
        )

        if material is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "material_type" in update_data:
            update_data["material_type"] = (
                update_data["material_type"].value
            )

        if "url" in update_data:
            update_data["url"] = str(
                update_data["url"]
            )

        return await self.material_repository.update(
            material,
            update_data,
        )

    async def delete(
        self,
        material_id: uuid.UUID,
    ) -> None:
        material = (
            await self.material_repository.get_by_id(
                material_id
            )
        )

        if material is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found",
            )

        await self.material_repository.delete(
            material
        )