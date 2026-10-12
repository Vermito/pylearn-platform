from prometheus_client import Counter


TASK_SUBMISSIONS_TOTAL = Counter(
    "pylearn_task_submissions_total",
    "Number of evaluated programming task submissions.",
    [
        "status",
        "difficulty",
    ],
)


TEST_SUBMISSIONS_TOTAL = Counter(
    "pylearn_test_submissions_total",
    "Number of completed knowledge test submissions.",
    [
        "passed",
    ],
)


for submission_status in (
    "success",
    "failed",
    "error",
    "timeout",
):
    for difficulty in (
        "easy",
        "medium",
        "hard",
    ):
        TASK_SUBMISSIONS_TOTAL.labels(
            status=submission_status,
            difficulty=difficulty,
        )


for passed in (
    "true",
    "false",
):
    TEST_SUBMISSIONS_TOTAL.labels(
        passed=passed
    )