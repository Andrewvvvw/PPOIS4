from minesweeper.scoring import CountdownTimer, compute_score


def test_compute_score_formula() -> None:
    score = compute_score(
        difficulty_base=500,
        revealed_safe=20,
        time_left=30,
        wrong_flags=2,
    )
    assert score == 820


def test_timer_countdown_and_expiration() -> None:
    timer = CountdownTimer(limit_seconds=3)
    timer.update(1.2)
    assert timer.seconds_left_int == 1
    timer.update(2.0)
    assert timer.is_expired
    assert timer.seconds_left_int == 0


def test_timer_ignores_negative_delta() -> None:
    timer = CountdownTimer(limit_seconds=10)
    timer.update(-2.0)
    assert timer.seconds_left_int == 10

