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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.material import Material
    from app.models.module import Module
    from app.models.task import Task
    from app.models.test import Test


class Topic(Base):
    __tablename__ = "topics"

    __table_args__ = (
        UniqueConstraint(
            "module_id",
            "position",
            name="uq_topics_module_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "modules.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    required_tasks_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    required_test_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
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

    module: Mapped["Module"] = relationship(
        back_populates="topics",
    )

    articles: Mapped[list["Article"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    materials: Mapped[list["Material"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    tests: Mapped[list["Test"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )