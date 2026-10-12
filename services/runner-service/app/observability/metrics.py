from prometheus_client import (
    Counter,
    Histogram,
)


CODE_EXECUTIONS_TOTAL = Counter(
    "pylearn_code_executions_total",
    "Number of Python sandbox executions.",
    [
        "status",
        "mode",
    ],
)


CODE_EXECUTION_DURATION_SECONDS = Histogram(
    "pylearn_code_execution_duration_seconds",
    (
        "Duration of Python sandbox "
        "executions in seconds."
    ),
    [
        "status",
        "mode",
    ],
    buckets=(
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.0,
        3.0,
        5.0,
        7.5,
        10.0,
    ),
)


for execution_status in (
    "success",
    "failed",
    "error",
    "timeout",
):
    for mode in (
        "function",
        "script",
    ):
        CODE_EXECUTIONS_TOTAL.labels(
            status=execution_status,
            mode=mode,
        )

        CODE_EXECUTION_DURATION_SECONDS.labels(
            status=execution_status,
            mode=mode,
        )