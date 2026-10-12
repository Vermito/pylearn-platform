import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
    )

    tasks_solved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    tests_completed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )