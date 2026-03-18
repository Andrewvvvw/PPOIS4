from pathlib import Path
import uuid

from minesweeper.records import Leaderboard


def _records_path() -> Path:
    return Path.cwd() / f"records_test_{uuid.uuid4().hex}.json"


def test_records_sorted_and_trimmed() -> None:
    path = _records_path()
    board = Leaderboard(path, max_entries=3)
    board.add_record("A", 50, "beginner", 10)
    board.add_record("B", 150, "beginner", 30)
    board.add_record("C", 70, "beginner", 20)
    board.add_record("D", 100, "beginner", 25)

    scores = [item.score for item in board.records]
    assert scores == [150, 100, 70]
    path.unlink(missing_ok=True)


def test_is_new_top_logic() -> None:
    path = _records_path()
    board = Leaderboard(path, max_entries=5)
    assert board.is_new_top(10)
    board.add_record("X", 100, "expert", 50)
    assert board.is_new_top(150)
    assert not board.is_new_top(90)
    path.unlink(missing_ok=True)
