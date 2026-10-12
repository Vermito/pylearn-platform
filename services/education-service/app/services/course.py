import uuid
from typing import Any

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.cache.redis import redis_cache
from app.models.course import Course
from app.models.enums import CourseLevel
from app.repositories.course import CourseRepository
from app.schemas.course import (
    CourseCreate,
    CourseDetailResponse,
    CourseUpdate,
)


class CourseService:
    def __init__(
        self,
        repository: CourseRepository,
    ):
        self.repository = repository

    async def create(
        self,
        data: CourseCreate,
    ) -> Course:
        course = await self.repository.create(
            title=data.title,
            description=data.description,
            level=data.level.value,
            is_published=data.is_published,
        )

        created_course = (
            await self.repository.get_by_id(
                course.id,
                published_only=False,
            )
        )

        if created_course is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Created course could not "
                    "be loaded"
                ),
            )

        await redis_cache.invalidate_courses()

        return created_course

    async def get_all(
        self,
        current_user: CurrentUser,
        *,
        limit: int,
        offset: int,
    ) -> list[Any]:
        published_only = (
            current_user.role != "admin"
        )

        version = (
            await redis_cache.get_courses_version()
        )

        cache_key: str | None = None

        if version is not None:
            cache_key = (
                redis_cache.build_courses_list_key(
                    version=version,
                    published_only=published_only,
                    limit=limit,
                    offset=offset,
                )
            )

            cached_courses = (
                await redis_cache.get_json(
                    cache_key
                )
            )

            if cached_courses is not None:
                return cached_courses

        courses = await self.repository.get_all(
            published_only=published_only,
            limit=limit,
            offset=offset,
        )

        # ORM → Pydantic → JSON-safe dict.
        # UUID и datetime становятся строками.
        response_data = [
            CourseDetailResponse
            .model_validate(course)
            .model_dump(mode="json")
            for course in courses
        ]

        if cache_key is not None:
            await redis_cache.set_json(
                cache_key,
                response_data,
            )

        return response_data

    async def get_by_id(
        self,
        course_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Course:
        published_only = (
            current_user.role != "admin"
        )

        course = await self.repository.get_by_id(
            course_id,
            published_only=published_only,
        )

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        return course

    async def update(
        self,
        course_id: uuid.UUID,
        data: CourseUpdate,
    ) -> Course:
        course = await self.repository.get_by_id(
            course_id,
            published_only=False,
        )

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if (
            "level" in update_data
            and isinstance(
                update_data["level"],
                CourseLevel,
            )
        ):
            update_data["level"] = (
                update_data["level"].value
            )

        await self.repository.update(
            course,
            update_data,
        )

        updated_course = (
            await self.repository.get_by_id(
                course_id,
                published_only=False,
            )
        )

        if updated_course is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Updated course could not "
                    "be loaded"
                ),
            )

        await redis_cache.invalidate_courses()

        return updated_course

    async def delete(
        self,
        course_id: uuid.UUID,
    ) -> None:
        course = await self.repository.get_by_id(
            course_id,
            published_only=False,
        )

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        await self.repository.delete(
            course
        )

        await redis_cache.invalidate_courses()