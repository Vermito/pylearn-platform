import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.models.enums import QuestionType
from app.schemas.test import (
    TestAnswer,
    TestSubmissionRequest,
)
from app.services.test import TestService


def create_service():
    repository = SimpleNamespace(
        get_by_id=AsyncMock(),
        get_progress_context=AsyncMock(),
    )

    publisher = SimpleNamespace(
        publish_test_completed=AsyncMock(),
    )

    service = TestService(
        repository=repository,
        event_publisher=publisher,
    )

    return (
        service,
        repository,
        publisher,
    )


def create_test_data():
    question_id = uuid.uuid4()

    correct_option_id = uuid.uuid4()
    wrong_option_id = uuid.uuid4()

    correct_option = SimpleNamespace(
        id=correct_option_id,
        is_correct=True,
    )

    wrong_option = SimpleNamespace(
        id=wrong_option_id,
        is_correct=False,
    )

    question = SimpleNamespace(
        id=question_id,
        question_type=(
            QuestionType
            .SINGLE_CHOICE.value
        ),
        options=[
            correct_option,
            wrong_option,
        ],
    )

    test = SimpleNamespace(
        id=uuid.uuid4(),
        passing_score=70,
        questions=[question],
    )

    return (
        test,
        question_id,
        correct_option_id,
        wrong_option_id,
    )


def test_single_choice_requires_exactly_one_correct_option():
    service, _, _ = create_service()

    service.validate_options(
        QuestionType.SINGLE_CHOICE.value,
        [
            {
                "answer_text": "A",
                "is_correct": True,
            },
            {
                "answer_text": "B",
                "is_correct": False,
            },
        ],
    )


def test_single_choice_rejects_two_correct_options():
    service, _, _ = create_service()

    with pytest.raises(
        HTTPException
    ) as exc_info:
        service.validate_options(
            QuestionType.SINGLE_CHOICE.value,
            [
                {
                    "answer_text": "A",
                    "is_correct": True,
                },
                {
                    "answer_text": "B",
                    "is_correct": True,
                },
            ],
        )

    assert exc_info.value.status_code == 400


def test_multiple_choice_requires_correct_option():
    service, _, _ = create_service()

    with pytest.raises(
        HTTPException
    ) as exc_info:
        service.validate_options(
            QuestionType.MULTIPLE_CHOICE.value,
            [
                {
                    "answer_text": "A",
                    "is_correct": False,
                },
                {
                    "answer_text": "B",
                    "is_correct": False,
                },
            ],
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_correct_test_submission_returns_100_percent():
    (
        service,
        repository,
        publisher,
    ) = create_service()

    (
        test,
        question_id,
        correct_option_id,
        _,
    ) = create_test_data()

    repository.get_by_id.return_value = test

    repository.get_progress_context.return_value = {
        "topic_id": uuid.uuid4(),
        "course_id": uuid.uuid4(),
        "next_topic_id": uuid.uuid4(),
        "required_tasks_count": 3,
        "required_test_score": 70,
    }

    current_user = SimpleNamespace(
        id=uuid.uuid4(),
        role="user",
    )

    request = TestSubmissionRequest(
        answers=[
            TestAnswer(
                question_id=question_id,
                option_ids=[
                    correct_option_id
                ],
            )
        ]
    )

    response = await service.submit(
        test_id=test.id,
        data=request,
        current_user=current_user,
    )

    assert response.score == 100
    assert response.correct_answers == 1
    assert response.total_questions == 1
    assert response.passed is True

    publisher.publish_test_completed.assert_awaited_once()

    event = (
        publisher
        .publish_test_completed
        .await_args
        .args[0]
    )

    assert event.payload.score == 100
    assert event.payload.passed is True

    assert (
        event.payload.user_id
        == current_user.id
    )


@pytest.mark.asyncio
async def test_wrong_answer_returns_zero_percent():
    (
        service,
        repository,
        publisher,
    ) = create_service()

    (
        test,
        question_id,
        _,
        wrong_option_id,
    ) = create_test_data()

    repository.get_by_id.return_value = test

    repository.get_progress_context.return_value = {
        "topic_id": uuid.uuid4(),
        "course_id": uuid.uuid4(),
        "next_topic_id": None,
        "required_tasks_count": 3,
        "required_test_score": 70,
    }

    current_user = SimpleNamespace(
        id=uuid.uuid4(),
        role="user",
    )

    request = TestSubmissionRequest(
        answers=[
            TestAnswer(
                question_id=question_id,
                option_ids=[
                    wrong_option_id
                ],
            )
        ]
    )

    response = await service.submit(
        test_id=test.id,
        data=request,
        current_user=current_user,
    )

    assert response.score == 0
    assert response.correct_answers == 0
    assert response.passed is False

    publisher.publish_test_completed.assert_awaited_once()


@pytest.mark.asyncio
async def test_submission_rejects_foreign_option():
    (
        service,
        repository,
        publisher,
    ) = create_service()

    (
        test,
        question_id,
        _,
        _,
    ) = create_test_data()

    repository.get_by_id.return_value = test

    current_user = SimpleNamespace(
        id=uuid.uuid4(),
        role="user",
    )

    request = TestSubmissionRequest(
        answers=[
            TestAnswer(
                question_id=question_id,
                option_ids=[
                    uuid.uuid4()
                ],
            )
        ]
    )

    with pytest.raises(
        HTTPException
    ) as exc_info:
        await service.submit(
            test_id=test.id,
            data=request,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400

    publisher.publish_test_completed.assert_not_awaited()


@pytest.mark.asyncio
async def test_submission_rejects_unknown_question():
    (
        service,
        repository,
        publisher,
    ) = create_service()

    (
        test,
        _,
        correct_option_id,
        _,
    ) = create_test_data()

    repository.get_by_id.return_value = test

    current_user = SimpleNamespace(
        id=uuid.uuid4(),
        role="user",
    )

    request = TestSubmissionRequest(
        answers=[
            TestAnswer(
                question_id=uuid.uuid4(),
                option_ids=[
                    correct_option_id
                ],
            )
        ]
    )

    with pytest.raises(
        HTTPException
    ) as exc_info:
        await service.submit(
            test_id=test.id,
            data=request,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400

    publisher.publish_test_completed.assert_not_awaited()