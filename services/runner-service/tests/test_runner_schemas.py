import pytest
from pydantic import ValidationError

from app.schemas.runner import (
    RunRequest,
    RunnerTestCase,
)


def test_function_mode_requires_entrypoint():
    with pytest.raises(
        ValidationError
    ):
        RunRequest(
            code=(
                "def square(n):\n"
                "    return n * n"
            ),
            mode="function",
            entrypoint=None,
            test_cases=[
                RunnerTestCase(
                    input_data="[2]",
                    expected_output="4",
                )
            ],
            time_limit_ms=2000,
            memory_limit_mb=128,
        )


def test_function_mode_accepts_entrypoint():
    request = RunRequest(
        code=(
            "def square(n):\n"
            "    return n * n"
        ),
        mode="function",
        entrypoint="square",
        test_cases=[
            RunnerTestCase(
                input_data="[2]",
                expected_output="4",
            )
        ],
        time_limit_ms=2000,
        memory_limit_mb=128,
    )

    assert request.entrypoint == "square"
    assert request.mode == "function"


def test_script_mode_does_not_require_entrypoint():
    request = RunRequest(
        code=(
            "n = int(input())\n"
            "print(n * n)"
        ),
        mode="script",
        entrypoint=None,
        test_cases=[
            RunnerTestCase(
                input_data="5",
                expected_output="25",
            )
        ],
        time_limit_ms=2000,
        memory_limit_mb=128,
    )

    assert request.entrypoint is None
    assert request.mode == "script"


def test_request_requires_at_least_one_test_case():
    with pytest.raises(
        ValidationError
    ):
        RunRequest(
            code="print('hello')",
            mode="script",
            entrypoint=None,
            test_cases=[],
            time_limit_ms=2000,
            memory_limit_mb=128,
        )


def test_memory_limit_is_validated():
    with pytest.raises(
        ValidationError
    ):
        RunRequest(
            code="print('hello')",
            mode="script",
            entrypoint=None,
            test_cases=[
                RunnerTestCase(
                    input_data="",
                    expected_output="hello",
                )
            ],
            time_limit_ms=2000,
            memory_limit_mb=1024,
        )


def test_time_limit_is_validated():
    with pytest.raises(
        ValidationError
    ):
        RunRequest(
            code="print('hello')",
            mode="script",
            entrypoint=None,
            test_cases=[
                RunnerTestCase(
                    input_data="",
                    expected_output="hello",
                )
            ],
            time_limit_ms=30_000,
            memory_limit_mb=128,
        )


def test_empty_code_is_rejected():
    with pytest.raises(
        ValidationError
    ):
        RunRequest(
            code="",
            mode="script",
            entrypoint=None,
            test_cases=[
                RunnerTestCase(
                    input_data="",
                    expected_output="hello",
                )
            ],
            time_limit_ms=2000,
            memory_limit_mb=128,
        )