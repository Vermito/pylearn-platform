import uuid

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.cache.redis import redis_cache
from app.models.module import Module
from app.repositories.course import CourseRepository
from app.repositories.module import ModuleRepository
from app.schemas.module import (
    ModuleCreate,
    ModuleUpdate,
)


class ModuleService:
    def __init__(
        self,
        module_repository: ModuleRepository,
        course_repository: CourseRepository,
    ):
        self.module_repository = (
            module_repository
        )

        self.course_repository = (
            course_repository
        )

    async def create(
        self,
        course_id: uuid.UUID,
        data: ModuleCreate,
    ) -> Module:
        module = (
            await self.module_repository.create(
                course_id=course_id,
                title=data.title,
                description=data.description,
            )
        )

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        created_module = (
            await self.module_repository.get_by_id(
                module.id,
                published_only=False,
            )
        )

        if created_module is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Created module could not "
                    "be loaded"
                ),
            )

        await redis_cache.invalidate_courses()

        return created_module

    async def get_by_course(
        self,
        course_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> list[Module]:
        published_only = (
            current_user.role != "admin"
        )

        course = (
            await self.course_repository.get_by_id(
                course_id,
                published_only=published_only,
            )
        )

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        return (
            await self.module_repository
            .get_by_course_id(
                course_id,
                published_only=published_only,
            )
        )

    async def update(
        self,
        module_id: uuid.UUID,
        data: ModuleUpdate,
    ) -> Module:
        module = (
            await self.module_repository.get_by_id(
                module_id,
                published_only=False,
            )
        )

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        await self.module_repository.update(
            module,
            update_data,
        )

        updated_module = (
            await self.module_repository.get_by_id(
                module_id,
                published_only=False,
            )
        )

        if updated_module is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Updated module could not "
                    "be loaded"
                ),
            )

        await redis_cache.invalidate_courses()

        return updated_module

    async def delete(
        self,
        module_id: uuid.UUID,
    ) -> None:
        module = (
            await self.module_repository.get_by_id(
                module_id,
                published_only=False,
            )
        )

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found",
            )

        await self.module_repository.delete(
            module
        )

        await redis_cache.invalidate_courses()