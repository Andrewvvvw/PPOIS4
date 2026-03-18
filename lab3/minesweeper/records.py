from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, UTC
import json
from pathlib import Path


@dataclass(slots=True)
class Record:
    name: str
    score: int
    difficulty: str
    time_left: int
    played_at: str


class Leaderboard:
    def __init__(self, path: Path, max_entries: int = 10):
        self.path = path
        self.max_entries = max_entries
        self._records: list[Record] = []
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self._records = []
            self.save()
            return
        with self.path.open("r", encoding="utf-8") as file_obj:
            raw = json.load(file_obj)
        self._records = [
            Record(
                name=item.get("name", "Unknown"),
                score=int(item.get("score", 0)),
                difficulty=item.get("difficulty", "unknown"),
                time_left=int(item.get("time_left", 0)),
                played_at=item.get("played_at", ""),
            )
            for item in raw
            if isinstance(item, dict)
        ]
        self._sort_trim()

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file_obj:
            json.dump([asdict(record) for record in self._records], file_obj, ensure_ascii=False, indent=2)

    def _sort_trim(self) -> None:
        self._records.sort(key=lambda record: record.score, reverse=True)
        self._records = self._records[: self.max_entries]

    @property
    def records(self) -> list[Record]:
        return list(self._records)

    @property
    def top_score(self) -> int | None:
        if not self._records:
            return None
        return self._records[0].score

    def is_new_top(self, score: int) -> bool:
        top = self.top_score
        if top is None:
            return True
        return score > top

    def add_record(
        self,
        name: str,
        score: int,
        difficulty: str,
        time_left: int,
        played_at: str | None = None,
    ) -> None:
        value = Record(
            name=name.strip() or "Player",
            score=int(score),
            difficulty=difficulty,
            time_left=int(time_left),
            played_at=played_at or datetime.now(UTC).isoformat(),
        )
        self._records.append(value)
        self._sort_trim()
        self.save()

