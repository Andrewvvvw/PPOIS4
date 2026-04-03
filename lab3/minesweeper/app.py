from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from dataclasses import dataclass
from typing import Any

from .audio import AudioManager
from .config import ConfigError, load_game_config, load_network_config, project_paths, records_path
from .records import Leaderboard
from .ui_scenes import MenuScene

@dataclass(slots=True)
class RuntimeState:
    running: bool = True


class MinesweeperApp:
    def __init__(self):
        self.paths = project_paths()
        self.game_config = load_game_config()
        self.network_config = load_network_config()
        records_cfg = self.game_config.get("records", {})
        self.leaderboard = Leaderboard(records_path(), int(records_cfg.get("max_entries", 10)))
        self.state = RuntimeState()
        self._font_cache: dict[tuple[int, bool], "pygame.font.Font"] = {}
        self._scene: "BaseScene | None" = None
        self._bootstrap_pygame()

    def _bootstrap_pygame(self) -> None:

        pygame.init()
        pygame.display.set_caption(self.game_config["window"]["title"])
        self.screen = pygame.display.set_mode(
            (int(self.game_config["window"]["width"]), int(self.game_config["window"]["height"]))
        )
        self.clock = pygame.time.Clock()
        self.audio = AudioManager(self.paths.root, self.game_config["audio"])
        self.audio.play_music()

    def font(self, size: int, bold: bool = False) -> "pygame.font.Font":

        key = (size, bold)
        cached = self._font_cache.get(key)
        if cached is not None:
            return cached
        font = pygame.font.SysFont("arial", size, bold=bold)
        self._font_cache[key] = font
        return font

    @property
    def scene(self) -> "BaseScene":
        if self._scene is None:
            raise RuntimeError("Scene is not initialized.")
        return self._scene

    def set_scene(self, scene: "BaseScene") -> None:
        self._scene = scene

    def run(self) -> None:

        self.set_scene(MenuScene(self))
        fps = int(self.game_config["fps"])

        while self.state.running:
            dt = self.clock.tick(fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False
                    break
                self.scene.handle_event(event)

            if not self.state.running:
                break

            self.scene.update(dt)
            if self.scene.next_scene is not None:
                self.set_scene(self.scene.next_scene)
                continue
            if self.scene.should_quit:
                self.state.running = False
                break

            self.scene.render(self.screen)
            pygame.display.flip()

        self.shutdown()

    def shutdown(self) -> None:
        try:
            self.audio.stop_music()
        except Exception:
            pass

        pygame.quit()


def run_game() -> int:
    try:
        app = MinesweeperApp()
    except ConfigError as exc:
        print(f"[CONFIG ERROR] {exc}")
        return 1
    except Exception as exc:
        print(f"[BOOT ERROR] {exc}")
        return 1

    app.run()
    return 0

if TYPE_CHECKING:
    from .game_scene import BaseScene