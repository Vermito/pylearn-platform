import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.models.enums import QuestionType


class AnswerOptionCreate(BaseModel):
    answer_text: str = Field(
        min_length=1,
        max_length=1000,
    )

    is_correct: bool = False


class AnswerOptionPublicResponse(BaseModel):
    id: uuid.UUID
    answer_text: str
    position: int

    model_config = ConfigDict(
        from_attributes=True
    )


class AnswerOptionAdminResponse(
    AnswerOptionPublicResponse
):
    is_correct: bool


class QuestionCreate(BaseModel):
    question_text: str = Field(
        min_length=3
    )

    question_type: QuestionType

    options: list[AnswerOptionCreate] = Field(
        min_length=2,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_correct_options(self):
        correct_count = sum(
            option.is_correct
            for option in self.options
        )

        if (
            self.question_type
            == QuestionType.SINGLE_CHOICE
            and correct_count != 1
        ):
            raise ValueError(
                "Single-choice question must have "
                "exactly one correct option"
            )

        if (
            self.question_type
            == QuestionType.MULTIPLE_CHOICE
            and correct_count < 1
        ):
            raise ValueError(
                "Multiple-choice question must have "
                "at least one correct option"
            )

        return self


class QuestionUpdate(BaseModel):
    question_text: str | None = Field(
        default=None,
        min_length=3,
    )

    question_type: QuestionType | None = None

    options: list[AnswerOptionCreate] | None = Field(
        default=None,
        min_length=2,
        max_length=20,
    )


class QuestionPublicResponse(BaseModel):
    id: uuid.UUID
    question_text: str
    question_type: QuestionType
    position: int

    options: list[
        AnswerOptionPublicResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class QuestionAdminResponse(BaseModel):
    id: uuid.UUID
    question_text: str
    question_type: QuestionType
    position: int

    options: list[
        AnswerOptionAdminResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class TestCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    passing_score: int = Field(
        default=70,
        ge=1,
        le=100,
    )

    is_published: bool = False


class TestUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = None

    passing_score: int | None = Field(
        default=None,
        ge=1,
        le=100,
    )

    is_published: bool | None = None


class TestPublicResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID

    title: str
    description: str | None

    passing_score: int
    is_published: bool

    created_at: datetime
    updated_at: datetime

    questions: list[
        QuestionPublicResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class TestAdminResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID

    title: str
    description: str | None

    passing_score: int
    is_published: bool

    created_at: datetime
    updated_at: datetime

    questions: list[
        QuestionAdminResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class TestAnswer(BaseModel):
    question_id: uuid.UUID

    option_ids: list[uuid.UUID] = Field(
        default_factory=list,
        max_length=20,
    )


class TestSubmissionRequest(BaseModel):
    answers: list[TestAnswer] = Field(
        default_factory=list,
        max_length=200,
    )


class TestSubmissionResponse(BaseModel):
    test_id: uuid.UUID

    score: int

    correct_answers: int
    total_questions: int

    passing_score: int

    passed: bool