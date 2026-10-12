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
    from app.models.question import Question


class AnswerOption(Base):
    __tablename__ = "answer_options"

    __table_args__ = (
        UniqueConstraint(
            "question_id",
            "position",
            name="uq_answer_options_question_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "questions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    answer_text: Mapped[str] = mapped_column(
        String(1000),
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

    question: Mapped["Question"] = relationship(
        back_populates="options",
    )