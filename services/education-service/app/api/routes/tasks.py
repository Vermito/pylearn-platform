import uuid

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
)
from app.clients.runner import RunnerClient
from app.db.database import get_db
from app.messaging.rabbitmq import (
    rabbitmq_publisher,
)
from app.models.enums import (
    TaskDifficulty,
    TaskType,
)
from app.repositories.task import TaskRepository
from app.schemas.submission import (
    TaskSubmissionRequest,
    TaskSubmissionResponse,
)
from app.schemas.task import (
    TaskAdminResponse,
    TaskCreate,
    TaskOptionAdminResponse,
    TaskOptionCreate,
    TaskPublicResponse,
    TaskUpdate,
    TestCaseAdminResponse,
    TestCaseCreate,
)
from app.services.submission import SubmissionService
from app.services.task import TaskService


router = APIRouter(
    tags=["Tasks"],
)


def get_task_service(
    db: AsyncSession,
) -> TaskService:
    return TaskService(
        TaskRepository(db)
    )


@router.post(
    "/topics/{topic_id}/tasks",
    response_model=TaskAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    topic_id: uuid.UUID,
    data: TaskCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).create(
        topic_id,
        data,
    )


@router.get(
    "/topics/{topic_id}/tasks",
    response_model=list[TaskPublicResponse],
)
async def get_tasks(
    topic_id: uuid.UUID,
    difficulty: TaskDifficulty | None = Query(
        default=None
    ),
    task_type: TaskType | None = Query(
        default=None
    ),
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).get_by_topic(
        topic_id=topic_id,
        current_user=current_user,
        difficulty=(
            difficulty.value
            if difficulty
            else None
        ),
        task_type=(
            task_type.value
            if task_type
            else None
        ),
    )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskPublicResponse,
)
async def get_task(
    task_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).get_by_id(
        task_id,
        current_user,
    )


@router.get(
    "/admin/tasks/{task_id}",
    response_model=TaskAdminResponse,
)
async def get_admin_task(
    task_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).get_by_id(
        task_id,
        current_user,
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskAdminResponse,
)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).update(
        task_id,
        data,
    )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await get_task_service(db).delete(task_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/tasks/{task_id}/test-cases",
    response_model=TestCaseAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_case(
    task_id: uuid.UUID,
    data: TestCaseCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).add_test_case(
        task_id,
        data,
    )


@router.post(
    "/tasks/{task_id}/options",
    response_model=TaskOptionAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task_option(
    task_id: uuid.UUID,
    data: TaskOptionCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_task_service(db).add_option(
        task_id,
        data,
    )


@router.post(
    "/tasks/{task_id}/submit",
    response_model=TaskSubmissionResponse,
)
async def submit_task(
    task_id: uuid.UUID,
    data: TaskSubmissionRequest,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = SubmissionService(
        task_repository=TaskRepository(db),
        runner_client=RunnerClient(),
        event_publisher=rabbitmq_publisher,
    )

    return await service.submit(
        task_id=task_id,
        data=data,
        current_user=current_user,
    )