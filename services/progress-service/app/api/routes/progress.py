import uuid
from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.db.database import get_db
from app.schemas.progress import (
    LeaderboardEntry,
    SolvedTaskResponse,
    TaskSubmissionResponse,
    UserProgressResponse,
    UserStatsResponse,
)
from app.services.progress_query import (
    ProgressQueryService,
)

router = APIRouter(
    tags=["Progress"],
)


@router.get(
    "/stats/me",
    response_model=UserStatsResponse,
)
async def get_my_stats(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressQueryService(db)

    return await service.get_stats(
        current_user.id
    )


@router.get(
    "/submissions/me",
    response_model=list[TaskSubmissionResponse],
)
async def get_my_submissions(
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
    service = ProgressQueryService(db)

    return await service.get_submissions(
        current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/solved-tasks/me",
    response_model=list[SolvedTaskResponse],
)
async def get_my_solved_tasks(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
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
    service = ProgressQueryService(db)

    return await service.get_solved_tasks(
        current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/leaderboard",
    response_model=list[LeaderboardEntry],
)
async def get_leaderboard(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressQueryService(db)

    return await service.get_leaderboard(
        limit=limit,
    )
    
@router.get(
    "/progress/me",
    response_model=list[UserProgressResponse],
)
async def get_my_progress(
    course_id: uuid.UUID | None = None,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProgressQueryService(db)

    return await service.get_progress(
        current_user.id,
        course_id=course_id,
    )