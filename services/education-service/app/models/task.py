import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.task_option import TaskOption
    from app.models.test_case import TestCase
    from app.models.topic import Topic


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "topics.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    task_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    starter_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    entrypoint: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    time_limit_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2000,
    )

    memory_limit_mb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=128,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    topic: Mapped["Topic"] = relationship(
        back_populates="tasks",
    )

    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )

    options: Mapped[list["TaskOption"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskOption.position",
    )