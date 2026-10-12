import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.db.database import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserRoleUpdate

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/users",
    response_model=list[UserResponse],
)
async def get_users(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    return await repository.get_all(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
async def update_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return await repository.update_role(
        user=user,
        role=data.role.value,
    )