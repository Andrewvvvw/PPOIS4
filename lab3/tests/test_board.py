from minesweeper.board import Board


def test_first_click_is_safe() -> None:
    board = Board(width=9, height=9, mines=10, seed=42)
    board.reveal(3, 3)
    assert not board.cell(3, 3).is_mine
    assert board.cell(3, 3).revealed


def test_seeded_layout_is_deterministic_for_same_first_click() -> None:
    board1 = Board(width=9, height=9, mines=10, seed=12345)
    board2 = Board(width=9, height=9, mines=10, seed=12345)

    board1.reveal(0, 0)
    board2.reveal(0, 0)

    assert board1.mine_positions() == board2.mine_positions()


def test_win_condition_after_revealing_all_safe_cells() -> None:
    board = Board(width=4, height=4, mines=2, seed=10)
    board.reveal(0, 0)
    for y in range(board.height):
        for x in range(board.width):
            if not board.cell(x, y).is_mine:
                board.reveal(x, y)

    assert board.is_win
    assert not board.is_loss

