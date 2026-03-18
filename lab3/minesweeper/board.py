from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Iterable


@dataclass(slots=True)
class Cell:
    is_mine: bool = False
    revealed: bool = False
    flagged: bool = False
    adjacent_mines: int = 0


@dataclass(slots=True)
class RevealResult:
    hit_mine: bool
    newly_revealed: int
    revealed_cells: list[tuple[int, int]]


class Board:
    def __init__(self, width: int, height: int, mines: int, seed: int | None = None):
        if width <= 0 or height <= 0:
            raise ValueError("Board dimensions must be positive.")
        if mines <= 0 or mines >= width * height:
            raise ValueError("Mines count must be > 0 and < width*height.")
        self.width = width
        self.height = height
        self.mines = mines
        self.seed = seed if seed is not None else random.SystemRandom().randrange(1, 2**31 - 1)
        self._rng = random.Random(self.seed)
        self.cells: list[list[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]
        self.generated = False
        self.first_move_done = False
        self.revealed_safe_count = 0
        self.exploded_at: tuple[int, int] | None = None
        self._total_safe = (self.width * self.height) - self.mines

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]

    def neighbors(self, x: int, y: int) -> Iterable[tuple[int, int]]:
        for ny in range(y - 1, y + 2):
            for nx in range(x - 1, x + 2):
                if nx == x and ny == y:
                    continue
                if self.is_in_bounds(nx, ny):
                    yield nx, ny

    def _generate_mines(self, first_click: tuple[int, int]) -> None:
        fx, fy = first_click
        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not (x == fx and y == fy)
        ]
        self._rng.shuffle(candidates)
        for mx, my in candidates[: self.mines]:
            self.cell(mx, my).is_mine = True
        self._recalculate_adjacent_counts()
        self.generated = True

    def _recalculate_adjacent_counts(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                current = self.cell(x, y)
                if current.is_mine:
                    current.adjacent_mines = -1
                    continue
                current.adjacent_mines = sum(
                    1 for nx, ny in self.neighbors(x, y) if self.cell(nx, ny).is_mine
                )

    def _relocate_mine(self, x: int, y: int) -> None:
        clicked = self.cell(x, y)
        if not clicked.is_mine:
            return
        clicked.is_mine = False
        for ty in range(self.height):
            for tx in range(self.width):
                if tx == x and ty == y:
                    continue
                target = self.cell(tx, ty)
                if not target.is_mine:
                    target.is_mine = True
                    self._recalculate_adjacent_counts()
                    return

    def toggle_flag(self, x: int, y: int) -> bool:
        if not self.is_in_bounds(x, y):
            return False
        target = self.cell(x, y)
        if target.revealed:
            return False
        target.flagged = not target.flagged
        return True

    def reveal(self, x: int, y: int) -> RevealResult:
        if not self.is_in_bounds(x, y):
            return RevealResult(hit_mine=False, newly_revealed=0, revealed_cells=[])

        target = self.cell(x, y)
        if target.flagged or target.revealed:
            return RevealResult(hit_mine=False, newly_revealed=0, revealed_cells=[])

        if not self.generated:
            self._generate_mines((x, y))

        if not self.first_move_done:
            self.first_move_done = True
            self._relocate_mine(x, y)

        target = self.cell(x, y)
        if target.is_mine:
            target.revealed = True
            self.exploded_at = (x, y)
            return RevealResult(hit_mine=True, newly_revealed=0, revealed_cells=[(x, y)])

        revealed_cells = self._flood_reveal(x, y)
        return RevealResult(
            hit_mine=False,
            newly_revealed=len(revealed_cells),
            revealed_cells=revealed_cells,
        )

    def _flood_reveal(self, x: int, y: int) -> list[tuple[int, int]]:
        queue: deque[tuple[int, int]] = deque([(x, y)])
        revealed_cells: list[tuple[int, int]] = []
        while queue:
            cx, cy = queue.popleft()
            current = self.cell(cx, cy)
            if current.revealed or current.flagged or current.is_mine:
                continue
            current.revealed = True
            self.revealed_safe_count += 1
            revealed_cells.append((cx, cy))
            if current.adjacent_mines != 0:
                continue
            for nx, ny in self.neighbors(cx, cy):
                neighbor = self.cell(nx, ny)
                if not neighbor.revealed and not neighbor.flagged and not neighbor.is_mine:
                    queue.append((nx, ny))
        return revealed_cells

    @property
    def is_win(self) -> bool:
        return self.revealed_safe_count == self._total_safe

    @property
    def is_loss(self) -> bool:
        return self.exploded_at is not None

    @property
    def flags_used(self) -> int:
        return sum(1 for row in self.cells for cell in row if cell.flagged)

    @property
    def wrong_flags(self) -> int:
        return sum(1 for row in self.cells for cell in row if cell.flagged and not cell.is_mine)

    def mine_positions(self) -> set[tuple[int, int]]:
        return {
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.cell(x, y).is_mine
        }

