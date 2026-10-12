import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ProgressStatus


class UserProgress(Base):
    __tablename__ = "user_progress"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "topic_id",
            name="uq_user_progress_user_topic",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ProgressStatus.IN_PROGRESS.value,
        index=True,
    )

    progress_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    solved_tasks_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    required_tasks_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    best_test_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    required_test_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )