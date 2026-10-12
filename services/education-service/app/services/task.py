import uuid

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.models.enums import TaskType
from app.models.task import Task
from app.models.task_option import TaskOption
from app.models.test_case import TestCase
from app.repositories.task import TaskRepository
from app.schemas.task import (
    TaskCreate,
    TaskOptionCreate,
    TaskUpdate,
    TestCaseCreate,
)


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
    ):
        self.repository = repository

    async def create(
        self,
        topic_id: uuid.UUID,
        data: TaskCreate,
    ) -> Task:
        task = await self.repository.create(
            topic_id=topic_id,
            title=data.title,
            description=data.description,
            difficulty=data.difficulty.value,
            task_type=data.task_type.value,
            starter_code=data.starter_code,
            entrypoint=data.entrypoint,
            time_limit_ms=data.time_limit_ms,
            memory_limit_mb=data.memory_limit_mb,
            is_published=data.is_published,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        created_task = await self.repository.get_by_id(
            task.id,
            published_only=False,
            include_hidden=True,
        )

        if created_task is None:
            raise HTTPException(
                status_code=500,
                detail="Created task could not be loaded",
            )

        return created_task

    async def get_by_id(
        self,
        task_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Task:
        is_admin = current_user.role == "admin"

        task = await self.repository.get_by_id(
            task_id,
            published_only=not is_admin,
            include_hidden=is_admin,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task

    async def get_by_topic(
        self,
        topic_id: uuid.UUID,
        current_user: CurrentUser,
        difficulty: str | None,
        task_type: str | None,
    ) -> list[Task]:
        is_admin = current_user.role == "admin"

        return await self.repository.get_by_topic_id(
            topic_id,
            published_only=not is_admin,
            include_hidden=is_admin,
            difficulty=difficulty,
            task_type=task_type,
        )

    async def update(
        self,
        task_id: uuid.UUID,
        data: TaskUpdate,
    ) -> Task:
        task = await self.repository.get_by_id(
            task_id,
            published_only=False,
            include_hidden=True,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "difficulty" in update_data:
            update_data["difficulty"] = (
                update_data["difficulty"].value
            )

        if "task_type" in update_data:
            update_data["task_type"] = (
                update_data["task_type"].value
            )

        await self.repository.update(
            task,
            update_data,
        )

        updated_task = await self.repository.get_by_id(
            task_id,
            published_only=False,
            include_hidden=True,
        )

        if updated_task is None:
            raise HTTPException(
                status_code=500,
                detail="Updated task could not be loaded",
            )

        return updated_task

    async def delete(
        self,
        task_id: uuid.UUID,
    ) -> None:
        task = await self.repository.get_by_id(
            task_id,
            published_only=False,
            include_hidden=True,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        await self.repository.delete(task)

    async def add_test_case(
        self,
        task_id: uuid.UUID,
        data: TestCaseCreate,
    ) -> TestCase:
        task = await self.repository.get_by_id(
            task_id,
            published_only=False,
            include_hidden=True,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.task_type == TaskType.MULTIPLE_CHOICE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Multiple-choice tasks use options, "
                    "not test cases"
                ),
            )

        return await self.repository.create_test_case(
            task_id=task_id,
            input_data=data.input_data,
            expected_output=data.expected_output,
            is_hidden=data.is_hidden,
        )

    async def add_option(
        self,
        task_id: uuid.UUID,
        data: TaskOptionCreate,
    ) -> TaskOption:
        task = await self.repository.get_by_id(
            task_id,
            published_only=False,
            include_hidden=True,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.task_type != TaskType.MULTIPLE_CHOICE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Options can only be added "
                    "to multiple-choice tasks"
                ),
            )

        option = await self.repository.create_option(
            task_id=task_id,
            text=data.text,
            is_correct=data.is_correct,
        )

        if option is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return option