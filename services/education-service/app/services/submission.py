import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser
from app.clients.runner import RunnerClient
from app.messaging.rabbitmq import RabbitMQPublisher
from app.models.enums import TaskType
from app.observability.metrics import (
    TASK_SUBMISSIONS_TOTAL,
)
from app.repositories.task import TaskRepository
from app.schemas.events import (
    TaskSubmissionEvaluatedEvent,
    TaskSubmissionPayload,
)
from app.schemas.runner import (
    RunnerRequest,
    RunnerTestCase,
)
from app.schemas.submission import (
    TaskSubmissionRequest,
    TaskSubmissionResponse,
    VisibleTestResult,
)


class SubmissionService:
    EXECUTABLE_TASK_TYPES = {
        TaskType.WRITE_CODE.value,
        TaskType.WRITE_FUNCTION.value,
        TaskType.PRACTICAL.value,
    }

    def __init__(
        self,
        task_repository: TaskRepository,
        runner_client: RunnerClient,
        event_publisher: RabbitMQPublisher,
    ):
        self.task_repository = task_repository
        self.runner_client = runner_client
        self.event_publisher = event_publisher

    async def submit(
        self,
        task_id: uuid.UUID,
        data: TaskSubmissionRequest,
        current_user: CurrentUser,
    ) -> TaskSubmissionResponse:
        task = await self.task_repository.get_by_id(
            task_id,
            published_only=True,
            include_hidden=True,
        )

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if (
            task.task_type
            not in self.EXECUTABLE_TASK_TYPES
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "This task type does not "
                    "support code submission"
                ),
            )

        if not task.test_cases:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Task has no test cases configured"
                ),
            )

        if (
            task.task_type
            == TaskType.WRITE_FUNCTION.value
        ):
            mode = "function"

            if not task.entrypoint:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "Task entrypoint "
                        "is not configured"
                    ),
                )

        else:
            mode = "script"

        runner_test_cases = [
            RunnerTestCase(
                input_data=test_case.input_data,
                expected_output=(
                    test_case.expected_output
                ),
            )
            for test_case in task.test_cases
        ]

        runner_request = RunnerRequest(
            code=data.code,
            mode=mode,
            entrypoint=task.entrypoint,
            test_cases=runner_test_cases,
            time_limit_ms=task.time_limit_ms,
            memory_limit_mb=task.memory_limit_mb,
        )

        runner_result = (
            await self.runner_client.run(
                runner_request
            )
        )

        TASK_SUBMISSIONS_TOTAL.labels(
            status=runner_result.status,
            difficulty=task.difficulty,
        ).inc()

        progress_context = (
            await self.task_repository
            .get_progress_context(
                task.id
            )
        )

        if progress_context is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "Task progress context "
                    "not found"
                ),
            )

        event = TaskSubmissionEvaluatedEvent(
            event_id=uuid.uuid4(),
            occurred_at=datetime.now(
                timezone.utc
            ),
            payload=TaskSubmissionPayload(
                user_id=current_user.id,
                task_id=task.id,
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
                code=data.code,
                status=runner_result.status,
                passed_tests=(
                    runner_result.passed_tests
                ),
                total_tests=(
                    runner_result.total_tests
                ),
                execution_time_ms=(
                    runner_result
                    .execution_time_ms
                ),
                difficulty=task.difficulty,
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
            .publish_task_submission(
                event
            )
        )

        visible_results: list[
            VisibleTestResult
        ] = []

        if (
            len(runner_result.cases)
            == len(task.test_cases)
        ):
            for test_case, case_result in zip(
                task.test_cases,
                runner_result.cases,
                strict=True,
            ):
                if test_case.is_hidden:
                    continue

                visible_results.append(
                    VisibleTestResult(
                        passed=(
                            case_result.passed
                        ),
                        input_data=(
                            case_result.input_data
                        ),
                        expected_output=(
                            case_result
                            .expected_output
                        ),
                        actual_output=(
                            case_result
                            .actual_output
                        ),
                        error=(
                            case_result.error
                        ),
                    )
                )

        general_error = None

        if (
            runner_result.status == "error"
            and runner_result.cases
        ):
            general_error = (
                runner_result.cases[0].error
            )

        return TaskSubmissionResponse(
            status=runner_result.status,
            passed=(
                runner_result.status
                == "success"
            ),
            passed_tests=(
                runner_result.passed_tests
            ),
            total_tests=(
                runner_result.total_tests
            ),
            execution_time_ms=(
                runner_result.execution_time_ms
            ),
            visible_tests=visible_results,
            error=general_error,
        )