import json
import logging

import aio_pika
from pydantic import ValidationError

from app.db.database import (
    async_session_factory,
)
from app.schemas.events import (
    TaskSubmissionEvaluatedEvent,
    TestCompletedEvent,
)
from app.services.submission_event import (
    SubmissionEventService,
)
from app.services.test_event import (
    TestEventService,
)


logger = logging.getLogger(__name__)


async def process_task_submission(
    message: (
        aio_pika.abc
        .AbstractIncomingMessage
    ),
) -> None:
    try:
        raw_data = json.loads(
            message.body.decode()
        )

        event = (
            TaskSubmissionEvaluatedEvent
            .model_validate(
                raw_data
            )
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ):
        logger.exception(
            "Invalid task submission event"
        )

        await message.reject(
            requeue=False
        )

        return

    try:
        async with (
            async_session_factory()
        ) as db:
            service = (
                SubmissionEventService(db)
            )

            await service.process(
                event
            )

        await message.ack()

    except Exception:
        logger.exception(
            "Task submission "
            "processing failed"
        )

        await message.nack(
            requeue=True
        )


async def process_test_completed(
    message: (
        aio_pika.abc
        .AbstractIncomingMessage
    ),
) -> None:
    try:
        raw_data = json.loads(
            message.body.decode()
        )

        event = (
            TestCompletedEvent
            .model_validate(
                raw_data
            )
        )

    except (
        json.JSONDecodeError,
        ValidationError,
    ):
        logger.exception(
            "Invalid test completed event"
        )

        await message.reject(
            requeue=False
        )

        return

    try:
        async with (
            async_session_factory()
        ) as db:
            service = TestEventService(
                db
            )

            await service.process(
                event
            )

        await message.ack()

    except Exception:
        logger.exception(
            "Test completed processing failed"
        )

        await message.nack(
            requeue=True
        )