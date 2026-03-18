from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RevealAnim:
    elapsed: float = 0.0
    duration: float = 0.3

    @property
    def done(self) -> bool:
        return self.elapsed >= self.duration

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)


@dataclass(slots=True)
class ExplosionAnim:
    active: bool = False
    elapsed: float = 0.0
    duration: float = 0.7
    center: tuple[int, int] = (0, 0)

    @property
    def progress(self) -> float:
        if not self.active or self.duration <= 0:
            return 0.0
        return min(1.0, self.elapsed / self.duration)


@dataclass(slots=True)
class PulseAnim:
    active: bool = False
    elapsed: float = 0.0
    duration: float = 1.2
    max_scale: float = 1.06

    @property
    def progress(self) -> float:
        if not self.active or self.duration <= 0:
            return 0.0
        return min(1.0, self.elapsed / self.duration)

    @property
    def scale(self) -> float:
        if not self.active:
            return 1.0
        p = self.progress
        if p >= 1.0:
            return 1.0
        if p < 0.5:
            return 1.0 + (self.max_scale - 1.0) * (p / 0.5)
        return self.max_scale - (self.max_scale - 1.0) * ((p - 0.5) / 0.5)


@dataclass(slots=True)
class AnimationState:
    reveal_duration: float
    explosion_duration: float
    win_pulse_duration: float
    win_pulse_scale: float
    reveal: dict[tuple[int, int], RevealAnim] = field(default_factory=dict)
    explosion: ExplosionAnim = field(default_factory=ExplosionAnim)
    pulse: PulseAnim = field(default_factory=PulseAnim)

    def add_reveal(self, cell: tuple[int, int]) -> None:
        self.reveal[cell] = RevealAnim(duration=self.reveal_duration)

    def trigger_explosion(self, center: tuple[int, int]) -> None:
        self.explosion = ExplosionAnim(
            active=True,
            elapsed=0.0,
            duration=self.explosion_duration,
            center=center,
        )

    def trigger_pulse(self) -> None:
        self.pulse = PulseAnim(
            active=True,
            elapsed=0.0,
            duration=self.win_pulse_duration,
            max_scale=self.win_pulse_scale,
        )

    def update(self, dt: float) -> None:
        finished = []
        for cell, anim in self.reveal.items():
            anim.elapsed += dt
            if anim.done:
                finished.append(cell)
        for cell in finished:
            self.reveal.pop(cell, None)

        if self.explosion.active:
            self.explosion.elapsed += dt
            if self.explosion.progress >= 1.0:
                self.explosion.active = False

        if self.pulse.active:
            self.pulse.elapsed += dt
            if self.pulse.progress >= 1.0:
                self.pulse.active = False

