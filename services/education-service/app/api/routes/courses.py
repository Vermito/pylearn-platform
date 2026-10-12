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
from app.db.database import get_db
from app.repositories.course import CourseRepository
from app.schemas.course import (
    CourseCreate,
    CourseDetailResponse,
    CourseUpdate,
)
from app.services.course import CourseService


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.get(
    "",
    response_model=list[CourseDetailResponse],
)
async def get_courses(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = CourseRepository(db)
    service = CourseService(repository)

    return await service.get_all(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
)
async def get_course(
    course_id: uuid.UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = CourseRepository(db)
    service = CourseService(repository)

    return await service.get_by_id(
        course_id=course_id,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=CourseDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    data: CourseCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = CourseRepository(db)
    service = CourseService(repository)

    return await service.create(data)


@router.patch(
    "/{course_id}",
    response_model=CourseDetailResponse,
)
async def update_course(
    course_id: uuid.UUID,
    data: CourseUpdate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = CourseRepository(db)
    service = CourseService(repository)

    return await service.update(
        course_id,
        data,
    )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course(
    course_id: uuid.UUID,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repository = CourseRepository(db)
    service = CourseService(repository)

    await service.delete(course_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )