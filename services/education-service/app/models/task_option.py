import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.task import Task


class TaskOption(Base):
    __tablename__ = "task_options"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "position",
            name="uq_task_options_task_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tasks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    task: Mapped["Task"] = relationship(
        back_populates="options",
    )