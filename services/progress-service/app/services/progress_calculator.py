def calculate_progress_percent(
    *,
    solved_tasks: int,
    required_tasks: int,
    best_test_score: int,
    required_test_score: int,
) -> int:
    if required_tasks > 0:
        tasks_ratio = min(
            solved_tasks / required_tasks,
            1,
        )
    else:
        tasks_ratio = 1

    if required_test_score > 0:
        test_ratio = min(
            best_test_score
            / required_test_score,
            1,
        )

        return round(
            (
                tasks_ratio * 0.5
                + test_ratio * 0.5
            )
            * 100
        )

    return round(
        tasks_ratio * 100
    )


def is_topic_completed(
    *,
    solved_tasks: int,
    required_tasks: int,
    best_test_score: int,
    required_test_score: int,
) -> bool:
    tasks_completed = (
        required_tasks == 0
        or solved_tasks >= required_tasks
    )

    test_completed = (
        required_test_score == 0
        or best_test_score
        >= required_test_score
    )

    return (
        tasks_completed
        and test_completed
    )