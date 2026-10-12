import uuid

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.cache.redis import redis_cache
from app.models.topic import Topic
from app.repositories.module import ModuleRepository
from app.repositories.topic import TopicRepository
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
)


class TopicService:
    def __init__(
        self,
        topic_repository: TopicRepository,
        module_repository: ModuleRepository,
    ):
        self.topic_repository = (
            topic_repository
        )

        self.module_repository = (
            module_repository
        )

    async def create(
        self,
        module_id: uuid.UUID,
        data: TopicCreate,
    ) -> Topic:
        topic = (
            await self.topic_repository.create(
                module_id=module_id,
                title=data.title,
                description=data.description,
                required_tasks_count=(
                    data.required_tasks_count
                ),
                required_test_score=(
                    data.required_test_score
                ),
                is_published=(
                    data.is_published
                ),
            )
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found",
            )

        await redis_cache.invalidate_courses()

        return topic

    async def get_by_module(
        self,
        module_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> list[Topic]:
        published_only = (
            current_user.role != "admin"
        )

        module = (
            await self.module_repository.get_by_id(
                module_id,
                published_only=published_only,
            )
        )

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found",
            )

        return (
            await self.topic_repository
            .get_by_module_id(
                module_id,
                published_only=published_only,
            )
        )

    async def get_by_id(
        self,
        topic_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Topic:
        published_only = (
            current_user.role != "admin"
        )

        topic = (
            await self.topic_repository.get_by_id(
                topic_id,
                published_only=published_only,
            )
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        return topic

    async def update(
        self,
        topic_id: uuid.UUID,
        data: TopicUpdate,
    ) -> Topic:
        topic = (
            await self.topic_repository.get_by_id(
                topic_id,
                published_only=False,
            )
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        updated_topic = (
            await self.topic_repository.update(
                topic,
                update_data,
            )
        )

        await redis_cache.invalidate_courses()

        return updated_topic

    async def delete(
        self,
        topic_id: uuid.UUID,
    ) -> None:
        topic = (
            await self.topic_repository.get_by_id(
                topic_id,
                published_only=False,
            )
        )

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        await self.topic_repository.delete(
            topic
        )

        await redis_cache.invalidate_courses()