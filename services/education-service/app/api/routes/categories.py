from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
)
from app.db.database import get_db
from app.repositories.category import CategoryRepository
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
)
from app.services.category import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
async def get_categories(
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(
        CategoryRepository(db)
    )

    return await service.get_all()


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(
        CategoryRepository(db)
    )

    return await service.create(data)