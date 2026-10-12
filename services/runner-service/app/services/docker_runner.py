import json
import subprocess
import time
import uuid

from app.schemas.runner import (
    RunRequest,
    RunResponse,
)


HARNESS = r"""
import contextlib
import io
import json
import signal
import sys
import traceback


class ExecutionTimeout(Exception):
    pass


def timeout_handler(signum, frame):
    raise ExecutionTimeout()


def normalize(value):
    return str(value).strip()


payload = json.loads(sys.stdin.read())

code = payload["code"]
mode = payload["mode"]
entrypoint = payload.get("entrypoint")
test_cases = payload["test_cases"]
time_limit = payload["time_limit_ms"] / 1000

results = []
passed_tests = 0


signal.signal(
    signal.SIGALRM,
    timeout_handler,
)

signal.setitimer(
    signal.ITIMER_REAL,
    time_limit,
)


try:
    compiled_code = compile(
        code,
        "<user_code>",
        "exec",
    )

    for case in test_cases:
        input_data = case.get("input_data")
        expected = normalize(
            case["expected_output"]
        )

        try:
            namespace = {}

            if mode == "function":
                stdout_buffer = io.StringIO()

                with contextlib.redirect_stdout(
                    stdout_buffer
                ):
                    exec(
                        compiled_code,
                        namespace,
                    )

                    function = namespace.get(
                        entrypoint
                    )

                    if not callable(function):
                        raise RuntimeError(
                            f"Function "
                            f"'{entrypoint}' "
                            f"not found"
                        )

                    raw_input = (
                        input_data
                        if input_data is not None
                        else "[]"
                    )

                    parsed_input = json.loads(
                        raw_input
                    )

                    if isinstance(
                        parsed_input,
                        list,
                    ):
                        result = function(
                            *parsed_input
                        )

                    elif isinstance(
                        parsed_input,
                        dict,
                    ):
                        result = function(
                            **parsed_input
                        )

                    else:
                        result = function(
                            parsed_input
                        )

                actual = normalize(result)

            else:
                stdin_buffer = io.StringIO(
                    input_data or ""
                )

                stdout_buffer = io.StringIO()

                old_stdin = sys.stdin
                sys.stdin = stdin_buffer

                try:
                    with contextlib.redirect_stdout(
                        stdout_buffer
                    ):
                        exec(
                            compiled_code,
                            {},
                        )
                finally:
                    sys.stdin = old_stdin

                actual = normalize(
                    stdout_buffer.getvalue()
                )

            passed = actual == expected

            if passed:
                passed_tests += 1

            results.append({
                "passed": passed,
                "input_data": input_data,
                "expected_output": expected,
                "actual_output": actual,
                "error": None,
            })

        except Exception as exc:
            results.append({
                "passed": False,
                "input_data": input_data,
                "expected_output": expected,
                "actual_output": None,
                "error": (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            })


    signal.setitimer(
        signal.ITIMER_REAL,
        0,
    )

    status = (
        "success"
        if passed_tests == len(test_cases)
        else "failed"
    )

    print(json.dumps({
        "status": status,
        "passed_tests": passed_tests,
        "total_tests": len(test_cases),
        "cases": results,
    }))


except ExecutionTimeout:
    print(json.dumps({
        "status": "timeout",
        "passed_tests": passed_tests,
        "total_tests": len(test_cases),
        "cases": results,
    }))


except Exception as exc:
    print(json.dumps({
        "status": "error",
        "passed_tests": passed_tests,
        "total_tests": len(test_cases),
        "cases": [{
            "passed": False,
            "input_data": None,
            "expected_output": "",
            "actual_output": None,
            "error": (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        }],
    }))
"""


class DockerRunner:
    IMAGE = "python:3.12-slim"

    def run(
        self,
        request: RunRequest,
    ) -> RunResponse:
        container_name = (
            f"pylearn-run-{uuid.uuid4().hex}"
        )

        payload = request.model_dump_json()

        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,

            "--network",
            "none",

            "--memory",
            f"{request.memory_limit_mb}m",

            "--memory-swap",
            f"{request.memory_limit_mb}m",

            "--cpus",
            "0.5",

            "--pids-limit",
            "32",

            "--read-only",

            "--cap-drop",
            "ALL",

            "--security-opt",
            "no-new-privileges=true",

            "--user",
            "65534:65534",

            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=16m",

            "-i",

            self.IMAGE,

            "python",
            "-I",
            "-c",
            HARNESS,
        ]

        started_at = time.perf_counter()

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )

            timeout_seconds = (
                request.time_limit_ms / 1000
                + 3
            )

            stdout, stderr = process.communicate(
                input=payload,
                timeout=timeout_seconds,
            )

        except subprocess.TimeoutExpired:
            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    container_name,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
            )

            elapsed = (
                time.perf_counter()
                - started_at
            ) * 1000

            return RunResponse(
                status="timeout",
                passed_tests=0,
                total_tests=len(
                    request.test_cases
                ),
                execution_time_ms=elapsed,
                cases=[],
            )

        elapsed = (
            time.perf_counter()
            - started_at
        ) * 1000

        if process.returncode != 0:
            return RunResponse(
                status="error",
                passed_tests=0,
                total_tests=len(
                    request.test_cases
                ),
                execution_time_ms=elapsed,
                cases=[],
            )

        try:
            data = json.loads(
                stdout.strip()
            )

        except json.JSONDecodeError:
            return RunResponse(
                status="error",
                passed_tests=0,
                total_tests=len(
                    request.test_cases
                ),
                execution_time_ms=elapsed,
                cases=[],
            )

        data["execution_time_ms"] = elapsed

        return RunResponse(**data)