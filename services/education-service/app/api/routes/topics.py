import uuid

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
)
from app.db.database import get_db
from app.repositories.module import ModuleRepository
from app.repositories.topic import TopicRepository
from app.schemas.topic import (
    TopicCreate,
    TopicResponse,
    TopicUpdate,
)
from app.services.topic import TopicService


router = APIRouter(
    tags=["Topics"],
)


def get_topic_service(
    db: AsyncSession,
) -> TopicService:
    return TopicService(
        TopicRepository(db),
        ModuleRepository(db),
    )


@router.post(
    "/modules/{module_id}/topics",
    response_model=TopicResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_topic(
    module_id: uuid.UUID,
    data: TopicCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_topic_service(db)

    return await service.create(
        module_id,
        data,
    )


@router.get(
    "/modules/{module_id}/topics",
    response_model=list[TopicResponse],
)
async def get_topics(
    module_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = get_topic_service(db)

    return await service.get_by_module(
        module_id,
        current_user,
    )


@router.get(
    "/topics/{topic_id}",
    response_model=TopicResponse,
)
async def get_topic(
    topic_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = get_topic_service(db)

    return await service.get_by_id(
        topic_id,
        current_user,
    )


@router.patch(
    "/topics/{topic_id}",
    response_model=TopicResponse,
)
async def update_topic(
    topic_id: uuid.UUID,
    data: TopicUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_topic_service(db)

    return await service.update(
        topic_id,
        data,
    )


@router.delete(
    "/topics/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_topic(
    topic_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_topic_service(db)

    await service.delete(topic_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )