from typing import Literal

from pydantic import BaseModel, Field


class TaskSubmissionRequest(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=50_000,
    )


class VisibleTestResult(BaseModel):
    passed: bool
    input_data: str | None
    expected_output: str
    actual_output: str | None = None
    error: str | None = None


class TaskSubmissionResponse(BaseModel):
    status: Literal[
        "success",
        "failed",
        "error",
        "timeout",
    ]

    passed: bool

    passed_tests: int
    total_tests: int

    execution_time_ms: float

    visible_tests: list[VisibleTestResult] = Field(
        default_factory=list
    )

    error: str | None = None