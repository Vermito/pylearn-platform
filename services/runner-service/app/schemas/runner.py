from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RunnerTestCase(BaseModel):
    input_data: str | None = None
    expected_output: str


class RunRequest(BaseModel):
    code: str = Field(
        min_length=1,
        max_length=50_000,
    )

    mode: Literal[
        "function",
        "script",
    ]

    entrypoint: str | None = Field(
        default=None,
        max_length=100,
    )

    test_cases: list[RunnerTestCase] = Field(
        min_length=1,
        max_length=30,
    )

    time_limit_ms: int = Field(
        default=2000,
        ge=100,
        le=5000,
    )

    memory_limit_mb: int = Field(
        default=128,
        ge=32,
        le=256,
    )

    @model_validator(mode="after")
    def validate_entrypoint(self):
        if (
            self.mode == "function"
            and not self.entrypoint
        ):
            raise ValueError(
                "entrypoint is required "
                "for function mode"
            )

        return self


class CaseResult(BaseModel):
    passed: bool

    input_data: str | None

    expected_output: str

    actual_output: str | None = None

    error: str | None = None


class RunResponse(BaseModel):
    status: Literal[
        "success",
        "failed",
        "error",
        "timeout",
    ]

    passed_tests: int

    total_tests: int

    execution_time_ms: float

    cases: list[CaseResult]