import uuid

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    require_admin,
)
from app.db.database import get_db
from app.messaging.rabbitmq import (
    rabbitmq_publisher,
)
from app.repositories.test import TestRepository
from app.schemas.test import (
    QuestionAdminResponse,
    QuestionCreate,
    QuestionUpdate,
    TestAdminResponse,
    TestCreate,
    TestPublicResponse,
    TestSubmissionRequest,
    TestSubmissionResponse,
    TestUpdate,
)
from app.services.test import TestService


router = APIRouter(
    tags=["Tests"],
)


def get_test_service(
    db: AsyncSession,
) -> TestService:
    return TestService(
        repository=TestRepository(db),
        event_publisher=rabbitmq_publisher,
    )


@router.post(
    "/topics/{topic_id}/tests",
    response_model=TestAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test(
    topic_id: uuid.UUID,
    data: TestCreate,
    _: CurrentUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).create(
        topic_id,
        data,
    )


@router.get(
    "/topics/{topic_id}/tests",
    response_model=list[TestPublicResponse],
)
async def get_topic_tests(
    topic_id: uuid.UUID,
    _: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).get_by_topic(
        topic_id,
        published_only=True,
    )


@router.get(
    "/admin/topics/{topic_id}/tests",
    response_model=list[TestAdminResponse],
)
async def get_admin_topic_tests(
    topic_id: uuid.UUID,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).get_by_topic(
        topic_id,
        published_only=False,
    )


@router.get(
    "/tests/{test_id}",
    response_model=TestPublicResponse,
)
async def get_test(
    test_id: uuid.UUID,
    _: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).get_public(
        test_id
    )


@router.get(
    "/admin/tests/{test_id}",
    response_model=TestAdminResponse,
)
async def get_admin_test(
    test_id: uuid.UUID,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).get_admin(
        test_id
    )


@router.patch(
    "/tests/{test_id}",
    response_model=TestAdminResponse,
)
async def update_test(
    test_id: uuid.UUID,
    data: TestUpdate,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).update(
        test_id,
        data,
    )


@router.delete(
    "/tests/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_test(
    test_id: uuid.UUID,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    await get_test_service(
        db
    ).delete(
        test_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/tests/{test_id}/questions",
    response_model=QuestionAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    test_id: uuid.UUID,
    data: QuestionCreate,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).create_question(
        test_id,
        data,
    )


@router.patch(
    "/questions/{question_id}",
    response_model=QuestionAdminResponse,
)
async def update_question(
    question_id: uuid.UUID,
    data: QuestionUpdate,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).update_question(
        question_id,
        data,
    )


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(
    question_id: uuid.UUID,
    _: CurrentUser = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(get_db),
):
    await get_test_service(
        db
    ).delete_question(
        question_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/tests/{test_id}/submit",
    response_model=TestSubmissionResponse,
)
async def submit_test(
    test_id: uuid.UUID,
    data: TestSubmissionRequest,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_test_service(
        db
    ).submit(
        test_id=test_id,
        data=data,
        current_user=current_user,
    )