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
from app.repositories.course import CourseRepository
from app.repositories.module import ModuleRepository
from app.schemas.module import (
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
)
from app.services.module import ModuleService


router = APIRouter(
    tags=["Modules"],
)


@router.post(
    "/courses/{course_id}/modules",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_module(
    course_id: uuid.UUID,
    data: ModuleCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    module_repository = ModuleRepository(db)
    course_repository = CourseRepository(db)

    service = ModuleService(
        module_repository,
        course_repository,
    )

    return await service.create(
        course_id,
        data,
    )


@router.get(
    "/courses/{course_id}/modules",
    response_model=list[ModuleResponse],
)
async def get_modules(
    course_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ModuleService(
        ModuleRepository(db),
        CourseRepository(db),
    )

    return await service.get_by_course(
        course_id,
        current_user,
    )


@router.patch(
    "/modules/{module_id}",
    response_model=ModuleResponse,
)
async def update_module(
    module_id: uuid.UUID,
    data: ModuleUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ModuleService(
        ModuleRepository(db),
        CourseRepository(db),
    )

    return await service.update(
        module_id,
        data,
    )


@router.delete(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_module(
    module_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ModuleService(
        ModuleRepository(db),
        CourseRepository(db),
    )

    await service.delete(module_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )