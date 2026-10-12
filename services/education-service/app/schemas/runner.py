from typing import Literal

from pydantic import BaseModel


class RunnerTestCase(BaseModel):
    input_data: str | None
    expected_output: str


class RunnerRequest(BaseModel):
    code: str
    mode: Literal["function", "script"]
    entrypoint: str | None

    test_cases: list[RunnerTestCase]

    time_limit_ms: int
    memory_limit_mb: int


class RunnerCaseResult(BaseModel):
    passed: bool

    input_data: str | None
    expected_output: str

    actual_output: str | None = None
    error: str | None = None


class RunnerResponse(BaseModel):
    status: Literal[
        "success",
        "failed",
        "error",
        "timeout",
    ]

    passed_tests: int
    total_tests: int
    execution_time_ms: float

    cases: list[RunnerCaseResult]