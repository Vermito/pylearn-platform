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
from app.repositories.material import MaterialRepository
from app.repositories.topic import TopicRepository
from app.schemas.material import (
    MaterialCreate,
    MaterialResponse,
    MaterialUpdate,
)
from app.services.material import MaterialService


router = APIRouter(
    tags=["Materials"],
)


def get_material_service(
    db: AsyncSession,
) -> MaterialService:
    return MaterialService(
        MaterialRepository(db),
        TopicRepository(db),
    )


@router.get(
    "/topics/{topic_id}/materials",
    response_model=list[MaterialResponse],
)
async def get_materials(
    topic_id: uuid.UUID,
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = get_material_service(db)

    return await service.get_by_topic(
        topic_id
    )


@router.post(
    "/topics/{topic_id}/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_material(
    topic_id: uuid.UUID,
    data: MaterialCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_material_service(db)

    return await service.create(
        topic_id,
        data,
    )


@router.patch(
    "/materials/{material_id}",
    response_model=MaterialResponse,
)
async def update_material(
    material_id: uuid.UUID,
    data: MaterialUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_material_service(db)

    return await service.update(
        material_id,
        data,
    )


@router.delete(
    "/materials/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_material(
    material_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = get_material_service(db)

    await service.delete(material_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )