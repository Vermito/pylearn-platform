import aio_pika

from app.core.config import settings
from app.schemas.events import (
    TaskSubmissionEvaluatedEvent,
    TestCompletedEvent,
)


EXCHANGE_NAME = "pylearn.events"

TASK_SUBMISSION_ROUTING_KEY = (
    "task.submission.evaluated"
)

TEST_COMPLETED_ROUTING_KEY = (
    "test.completed"
)


class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self) -> None:
        self.connection = (
            await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
        )

        self.channel = (
            await self.connection.channel()
        )

        self.exchange = (
            await self.channel.declare_exchange(
                EXCHANGE_NAME,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
        )

    async def _publish(
        self,
        *,
        body: bytes,
        routing_key: str,
        event_id: str,
        event_type: str,
    ) -> None:
        if self.exchange is None:
            raise RuntimeError(
                "RabbitMQ publisher "
                "is not connected"
            )

        message = aio_pika.Message(
            body=body,
            content_type="application/json",
            delivery_mode=(
                aio_pika.DeliveryMode.PERSISTENT
            ),
            message_id=event_id,
            type=event_type,
        )

        await self.exchange.publish(
            message,
            routing_key=routing_key,
        )

    async def publish_task_submission(
        self,
        event: TaskSubmissionEvaluatedEvent,
    ) -> None:
        await self._publish(
            body=(
                event.model_dump_json().encode()
            ),
            routing_key=(
                TASK_SUBMISSION_ROUTING_KEY
            ),
            event_id=str(event.event_id),
            event_type=event.event_type,
        )

    async def publish_test_completed(
        self,
        event: TestCompletedEvent,
    ) -> None:
        await self._publish(
            body=(
                event.model_dump_json().encode()
            ),
            routing_key=(
                TEST_COMPLETED_ROUTING_KEY
            ),
            event_id=str(event.event_id),
            event_type=event.event_type,
        )

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()


rabbitmq_publisher = RabbitMQPublisher()