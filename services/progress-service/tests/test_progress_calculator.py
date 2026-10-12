from app.services.progress_calculator import (
    calculate_progress_percent,
    is_topic_completed,
)


def test_progress_one_of_three_tasks_with_test():
    result = calculate_progress_percent(
        solved_tasks=1,
        required_tasks=3,
        best_test_score=0,
        required_test_score=70,
    )

    assert result == 17


def test_progress_all_tasks_without_test_completed():
    result = calculate_progress_percent(
        solved_tasks=3,
        required_tasks=3,
        best_test_score=0,
        required_test_score=70,
    )

    assert result == 50


def test_progress_all_tasks_and_required_test_score():
    result = calculate_progress_percent(
        solved_tasks=3,
        required_tasks=3,
        best_test_score=70,
        required_test_score=70,
    )

    assert result == 100


def test_progress_is_capped_at_100():
    result = calculate_progress_percent(
        solved_tasks=10,
        required_tasks=3,
        best_test_score=100,
        required_test_score=70,
    )

    assert result == 100


def test_progress_without_required_test():
    result = calculate_progress_percent(
        solved_tasks=2,
        required_tasks=4,
        best_test_score=0,
        required_test_score=0,
    )

    assert result == 50


def test_topic_is_completed():
    result = is_topic_completed(
        solved_tasks=3,
        required_tasks=3,
        best_test_score=85,
        required_test_score=70,
    )

    assert result is True


def test_topic_is_not_completed_when_test_failed():
    result = is_topic_completed(
        solved_tasks=3,
        required_tasks=3,
        best_test_score=60,
        required_test_score=70,
    )

    assert result is False


def test_topic_is_not_completed_when_tasks_missing():
    result = is_topic_completed(
        solved_tasks=2,
        required_tasks=3,
        best_test_score=100,
        required_test_score=70,
    )

    assert result is False