import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material


class MaterialRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        *,
        topic_id: uuid.UUID,
        title: str,
        description: str | None,
        material_type: str,
        url: str,
    ) -> Material:
        material = Material(
            topic_id=topic_id,
            title=title,
            description=description,
            material_type=material_type,
            url=url,
        )

        self.db.add(material)

        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def get_by_id(
        self,
        material_id: uuid.UUID,
    ) -> Material | None:
        result = await self.db.execute(
            select(Material).where(
                Material.id == material_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_topic_id(
        self,
        topic_id: uuid.UUID,
    ) -> list[Material]:
        result = await self.db.execute(
            select(Material)
            .where(
                Material.topic_id == topic_id
            )
            .order_by(
                Material.created_at
            )
        )

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        material: Material,
        data: dict[str, Any],
    ) -> Material:
        for field, value in data.items():
            setattr(
                material,
                field,
                value,
            )

        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def delete(
        self,
        material: Material,
    ) -> None:
        await self.db.delete(material)
        await self.db.commit()