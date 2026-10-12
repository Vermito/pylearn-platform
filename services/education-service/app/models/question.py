import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.answer_option import AnswerOption
    from app.models.test import Test


class Question(Base):
    __tablename__ = "questions"

    __table_args__ = (
        UniqueConstraint(
            "test_id",
            "position",
            name="uq_questions_test_position",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    test_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tests.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    test: Mapped["Test"] = relationship(
        back_populates="questions",
    )

    options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="AnswerOption.position",
    )