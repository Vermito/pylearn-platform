import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.solved_task import SolvedTask
from app.models.task_submission import TaskSubmission
from app.models.user_progress import UserProgress
from app.models.user_stats import UserStats
from app.repositories.progress import ProgressRepository
from app.schemas.progress import LeaderboardEntry


class ProgressQueryService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.repository = ProgressRepository(db)

    async def get_stats(
        self,
        user_id: uuid.UUID,
    ) -> UserStats:
        stats = await self.repository.get_stats(
            user_id
        )

        if stats is not None:
            return stats

        stats = (
            await self.repository.get_or_create_stats(
                user_id
            )
        )

        await self.db.commit()
        await self.db.refresh(stats)

        return stats

    async def get_submissions(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[TaskSubmission]:
        return await self.repository.get_submissions(
            user_id,
            limit=limit,
            offset=offset,
        )

    async def get_solved_tasks(
        self,
        user_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[SolvedTask]:
        return await self.repository.get_solved_tasks(
            user_id,
            limit=limit,
            offset=offset,
        )

    async def get_leaderboard(
        self,
        *,
        limit: int,
    ) -> list[LeaderboardEntry]:
        stats = await self.repository.get_leaderboard(
            limit=limit
        )

        return [
            LeaderboardEntry(
                position=index,
                user_id=item.user_id,
                xp=item.xp,
                tasks_solved=item.tasks_solved,
                current_streak=item.current_streak,
            )
            for index, item in enumerate(
                stats,
                start=1,
            )
        ]

    async def get_progress(
        self,
        user_id: uuid.UUID,
        *,
        course_id: uuid.UUID | None,
    ) -> list[UserProgress]:
        return await self.repository.get_user_progress(
            user_id,
            course_id=course_id,
        )