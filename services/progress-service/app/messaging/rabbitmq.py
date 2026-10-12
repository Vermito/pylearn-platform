import aio_pika

from app.core.config import settings
from app.messaging.consumers import (
    process_task_submission,
    process_test_completed,
)


EXCHANGE_NAME = "pylearn.events"

TASK_SUBMISSION_ROUTING_KEY = (
    "task.submission.evaluated"
)

TEST_COMPLETED_ROUTING_KEY = (
    "test.completed"
)

TASK_SUBMISSION_QUEUE = (
    "progress.task_submissions"
)

TEST_COMPLETED_QUEUE = (
    "progress.test_results"
)


class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        self.connection = (
            await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
        )

        self.channel = (
            await self.connection.channel()
        )

        await self.channel.set_qos(
            prefetch_count=10
        )

        exchange = (
            await self.channel
            .declare_exchange(
                EXCHANGE_NAME,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
        )

        task_queue = (
            await self.channel
            .declare_queue(
                TASK_SUBMISSION_QUEUE,
                durable=True,
            )
        )

        await task_queue.bind(
            exchange,
            routing_key=(
                TASK_SUBMISSION_ROUTING_KEY
            ),
        )

        await task_queue.consume(
            process_task_submission
        )

        test_queue = (
            await self.channel
            .declare_queue(
                TEST_COMPLETED_QUEUE,
                durable=True,
            )
        )

        await test_queue.bind(
            exchange,
            routing_key=(
                TEST_COMPLETED_ROUTING_KEY
            ),
        )

        await test_queue.consume(
            process_test_completed
        )

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()


rabbitmq_consumer = RabbitMQConsumer()