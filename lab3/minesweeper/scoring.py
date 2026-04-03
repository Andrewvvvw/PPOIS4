from __future__ import annotations
from dataclasses import dataclass


def compute_score(
    difficulty_base: int,
    revealed_safe: int,
    time_left: int,
    wrong_flags: int,
) -> int:
    score = difficulty_base + (revealed_safe * 10) + (max(time_left, 0) * 5) - (wrong_flags * 15)
    return int(score)


@dataclass(slots=True)
class CountdownTimer:
    limit_seconds: int
    remaining_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.limit_seconds <= 0:
            raise ValueError("Timer limit must be positive.")
        if self.remaining_seconds <= 0:
            self.remaining_seconds = float(self.limit_seconds)

    @property
    def is_expired(self) -> bool:
        return self.remaining_seconds <= 0.0

    def update(self, delta_seconds: float) -> None:
        if delta_seconds < 0:
            return
        if self.is_expired:
            self.remaining_seconds = 0.0
            return
        self.remaining_seconds = max(0.0, self.remaining_seconds - delta_seconds)

    @property
    def seconds_left_int(self) -> int:
        return int(self.remaining_seconds)

