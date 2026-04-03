from __future__ import annotations

from pathlib import Path
from typing import Any
import pygame


class AudioManager:
    def __init__(self, root: Path, audio_config: dict[str, Any]):
        self.root = root
        self.audio_config = audio_config
        self.available = False
        self.sounds: dict[str, "pygame.mixer.Sound"] = {}
        self._music_path: Path | None = None
        self._init()

    def _init(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False
            return

        sound_cfg = self.audio_config.get("sounds", {})
        volume = float(self.audio_config.get("sound_volume", 1.0))
        master = float(self.audio_config.get("master_volume", 1.0))
        for name, rel_path in sound_cfg.items():
            file_path = self.root / rel_path
            try:
                sound = pygame.mixer.Sound(str(file_path))
                sound.set_volume(max(0.0, min(1.0, volume * master)))
                self.sounds[name] = sound
            except pygame.error:
                continue

        music_rel = self.audio_config.get("music")
        if isinstance(music_rel, str):
            self._music_path = self.root / music_rel

    def play(self, name: str) -> None:
        if not self.available:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self) -> None:
        if not self.available or self._music_path is None:
            return

        try:
            pygame.mixer.music.load(str(self._music_path))
            volume = float(self.audio_config.get("music_volume", 0.5))
            master = float(self.audio_config.get("master_volume", 1.0))
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume * master)))
            pygame.mixer.music.play(-1)
        except pygame.error:
            return

    def stop_music(self) -> None:
        if not self.available:
            return

        pygame.mixer.music.stop()
