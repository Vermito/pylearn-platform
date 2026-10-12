import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TestResult(Base):
    __tablename__ = "test_results"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            name="uq_test_results_event_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    test_id: Mapped[uuid.UUID] = mapped_column(
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

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )