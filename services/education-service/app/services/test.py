import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.messaging.rabbitmq import RabbitMQPublisher
from app.models.enums import QuestionType
from app.models.question import Question
from app.models.test import Test
from app.observability.metrics import (
    TEST_SUBMISSIONS_TOTAL,
)
from app.repositories.test import TestRepository
from app.schemas.events import (
    TestCompletedEvent,
    TestCompletedPayload,
)
from app.schemas.test import (
    QuestionCreate,
    QuestionUpdate,
    TestCreate,
    TestSubmissionRequest,
    TestSubmissionResponse,
    TestUpdate,
)


class TestService:
    def __init__(
        self,
        repository: TestRepository,
        event_publisher: RabbitMQPublisher,
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    @staticmethod
    def validate_options(
        question_type: str,
        options: list[dict],
    ) -> None:
        correct_count = sum(
            option["is_correct"]
            for option in options
        )

        if (
            question_type
            == QuestionType.SINGLE_CHOICE.value
            and correct_count != 1
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Single-choice question must "
                    "have exactly one correct option"
                ),
            )

        if (
            question_type
            == QuestionType.MULTIPLE_CHOICE.value
            and correct_count < 1
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Multiple-choice question must "
                    "have at least one correct option"
                ),
            )

    async def create(
        self,
        topic_id: uuid.UUID,
        data: TestCreate,
    ) -> Test:
        test = await self.repository.create(
            topic_id=topic_id,
            title=data.title,
            description=data.description,
            passing_score=data.passing_score,
            is_published=data.is_published,
        )

        if test is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found",
            )

        created = (
            await self.repository.get_by_id(
                test.id,
                published_only=False,
            )
        )

        if created is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Created test could not "
                    "be loaded"
                ),
            )

        return created

    async def get_public(
        self,
        test_id: uuid.UUID,
    ) -> Test:
        test = await self.repository.get_by_id(
            test_id,
            published_only=True,
        )

        if test is None:
            raise HTTPException(
                status_code=404,
                detail="Test not found",
            )

        return test

    async def get_admin(
        self,
        test_id: uuid.UUID,
    ) -> Test:
        test = await self.repository.get_by_id(
            test_id,
            published_only=False,
        )

        if test is None:
            raise HTTPException(
                status_code=404,
                detail="Test not found",
            )

        return test

    async def get_by_topic(
        self,
        topic_id: uuid.UUID,
        *,
        published_only: bool,
    ) -> list[Test]:
        return (
            await self.repository
            .get_by_topic_id(
                topic_id,
                published_only=published_only,
            )
        )

    async def update(
        self,
        test_id: uuid.UUID,
        data: TestUpdate,
    ) -> Test:
        test = await self.get_admin(
            test_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        await self.repository.update(
            test,
            update_data,
        )

        updated = (
            await self.repository.get_by_id(
                test_id,
                published_only=False,
            )
        )

        if updated is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Updated test could not "
                    "be loaded"
                ),
            )

        return updated

    async def delete(
        self,
        test_id: uuid.UUID,
    ) -> None:
        test = await self.get_admin(
            test_id
        )

        await self.repository.delete(
            test
        )

    async def create_question(
        self,
        test_id: uuid.UUID,
        data: QuestionCreate,
    ) -> Question:
        options = [
            option.model_dump()
            for option in data.options
        ]

        self.validate_options(
            data.question_type.value,
            options,
        )

        question = (
            await self.repository
            .create_question(
                test_id=test_id,
                question_text=(
                    data.question_text
                ),
                question_type=(
                    data.question_type.value
                ),
                options=options,
            )
        )

        if question is None:
            raise HTTPException(
                status_code=404,
                detail="Test not found",
            )

        return question

    async def update_question(
        self,
        question_id: uuid.UUID,
        data: QuestionUpdate,
    ) -> Question:
        question = (
            await self.repository
            .get_question_by_id(
                question_id
            )
        )

        if question is None:
            raise HTTPException(
                status_code=404,
                detail="Question not found",
            )

        question_type = (
            data.question_type.value
            if data.question_type is not None
            else question.question_type
        )

        options = None

        if data.options is not None:
            options = [
                option.model_dump()
                for option in data.options
            ]

            self.validate_options(
                question_type,
                options,
            )

        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"options"},
        )

        if "question_type" in update_data:
            update_data["question_type"] = (
                question_type
            )

        return (
            await self.repository
            .update_question(
                question,
                data=update_data,
                options=options,
            )
        )

    async def delete_question(
        self,
        question_id: uuid.UUID,
    ) -> None:
        question = (
            await self.repository
            .get_question_by_id(
                question_id
            )
        )

        if question is None:
            raise HTTPException(
                status_code=404,
                detail="Question not found",
            )

        await self.repository.delete_question(
            question
        )

    async def submit(
        self,
        test_id: uuid.UUID,
        data: TestSubmissionRequest,
        current_user: CurrentUser,
    ) -> TestSubmissionResponse:
        test = await self.get_public(
            test_id
        )

        if not test.questions:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Test has no questions "
                    "configured"
                ),
            )

        question_ids = [
            answer.question_id
            for answer in data.answers
        ]

        if (
            len(question_ids)
            != len(set(question_ids))
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Duplicate question answers "
                    "are not allowed"
                ),
            )

        known_questions = {
            question.id: question
            for question in test.questions
        }

        answer_map = {
            answer.question_id: set(
                answer.option_ids
            )
            for answer in data.answers
        }

        unknown_questions = (
            set(answer_map)
            - set(known_questions)
        )

        if unknown_questions:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Answer contains "
                    "unknown question"
                ),
            )

        correct_answers = 0

        for question in test.questions:
            selected = answer_map.get(
                question.id,
                set(),
            )

            valid_option_ids = {
                option.id
                for option in question.options
            }

            if not selected.issubset(
                valid_option_ids
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Answer contains option "
                        "that does not belong "
                        "to the question"
                    ),
                )

            expected = {
                option.id
                for option in question.options
                if option.is_correct
            }

            if selected == expected:
                correct_answers += 1

        total_questions = len(
            test.questions
        )

        score = round(
            correct_answers
            / total_questions
            * 100
        )

        passed = (
            score >= test.passing_score
        )

        TEST_SUBMISSIONS_TOTAL.labels(
            passed=(
                "true"
                if passed
                else "false"
            )
        ).inc()

        progress_context = (
            await self.repository
            .get_progress_context(
                test.id
            )
        )

        if progress_context is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Test progress context "
                    "could not be loaded"
                ),
            )

        event = TestCompletedEvent(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(
                timezone.utc
            ),
            payload=TestCompletedPayload(
                user_id=current_user.id,
                test_id=test.id,
                topic_id=(
                    progress_context[
                        "topic_id"
                    ]
                ),
                course_id=(
                    progress_context[
                        "course_id"
                    ]
                ),
                next_topic_id=(
                    progress_context[
                        "next_topic_id"
                    ]
                ),
                score=score,
                correct_answers=(
                    correct_answers
                ),
                total_questions=(
                    total_questions
                ),
                passed=passed,
                required_tasks_count=(
                    progress_context[
                        "required_tasks_count"
                    ]
                ),
                required_test_score=(
                    progress_context[
                        "required_test_score"
                    ]
                ),
            ),
        )

        await (
            self.event_publisher
            .publish_test_completed(
                event
            )
        )

        return TestSubmissionResponse(
            test_id=test.id,
            score=score,
            correct_answers=(
                correct_answers
            ),
            total_questions=(
                total_questions
            ),
            passing_score=(
                test.passing_score
            ),
            passed=passed,
        )