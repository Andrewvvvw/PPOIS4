from __future__ import annotations

import random
from typing import Any

import pygame
import pygame_gui

from .animations import AnimationState
from .board import Board
from .network import NetworkPeer
from .protocol import arbitrate_winner
from .scoring import CountdownTimer, compute_score


def _draw_centered_text(
    surface: "pygame.Surface",
    font: "pygame.font.Font",
    text: str,
    color: tuple[int, int, int],
    y: int,
) -> None:
    render = font.render(text, True, color)
    rect = render.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(render, rect)


def _format_timer(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def _ui_scenes():
    from . import ui_scenes

    return ui_scenes


class BaseScene:
    _fonts_preloaded = False

    def __init__(self, app: "MinesweeperApp"):
        self.app = app
        self.next_scene: BaseScene | None = None
        self.should_quit = False
        theme_path = self.app.paths.root / "assets" / "ui_theme.json"
        if theme_path.exists():
            self.ui_manager = pygame_gui.UIManager(app.screen.get_size(), str(theme_path))
        else:
            self.ui_manager = pygame_gui.UIManager(app.screen.get_size())
        if not BaseScene._fonts_preloaded:
            try:
                self.ui_manager.add_font_paths("arial", "C:/Windows/Fonts/arial.ttf")
                self.ui_manager.preload_fonts(
                    [
                        {"name": "arial", "point_size": 18, "style": "regular", "antialiased": 1},
                        {"name": "arial", "point_size": 18, "style": "bold", "antialiased": 1},
                        {"name": "arial", "point_size": 20, "style": "regular", "antialiased": 1},
                        {"name": "arial", "point_size": 20, "style": "bold", "antialiased": 1},
                    ]
                )
            except Exception:
                pass
            BaseScene._fonts_preloaded = True

    def switch(self, scene: "BaseScene") -> None:
        self.next_scene = scene

    def handle_event(self, event: "pygame.event.Event") -> None:
        raise NotImplementedError

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def render(self, screen: "pygame.Surface") -> None:
        raise NotImplementedError


class GameScene(BaseScene):
    NUMBER_COLORS = {
        1: (37, 99, 235),
        2: (22, 163, 74),
        3: (220, 38, 38),
        4: (79, 70, 229),
        5: (147, 51, 234),
        6: (8, 145, 178),
        7: (75, 85, 99),
        8: (17, 24, 39),
    }

    def __init__(
        self,
        app: "MinesweeperApp",
        mode: str,
        difficulty_key: str,
        seed: int | None = None,
        time_limit_override: int | None = None,
        peer: NetworkPeer | None = None,
        role: str = "",
        local_name: str = "",
        remote_name: str = "",
    ):
        super().__init__(app)
        self.mode = mode
        self.difficulty_key = difficulty_key
        self.diff_cfg = self.app.game_config["difficulties"][difficulty_key]
        self.seed = seed if seed is not None else random.SystemRandom().randrange(1, 2**31 - 1)
        self.board = Board(
            width=int(self.diff_cfg["width"]),
            height=int(self.diff_cfg["height"]),
            mines=int(self.diff_cfg["mines"]),
            seed=self.seed,
        )
        time_limit = int(time_limit_override if time_limit_override is not None else self.diff_cfg["time_limit"])
        self.timer = CountdownTimer(time_limit)
        anim_cfg = self.app.game_config["animations"]
        self.animations = AnimationState(
            reveal_duration=float(anim_cfg["reveal_duration"]),
            explosion_duration=float(anim_cfg["explosion_duration"]),
            win_pulse_duration=float(anim_cfg["win_pulse_duration"]),
            win_pulse_scale=float(anim_cfg["win_pulse_scale"]),
        )
        self.result_state = "running"
        self.elapsed = 0.0
        self.peer = peer
        self.role = role
        self.local_name = local_name
        self.remote_name = remote_name
        self.remote_state: dict[str, Any] | None = None
        self.remote_report: dict[str, Any] | None = None
        self.local_report: dict[str, Any] | None = None
        self.match_result: dict[str, Any] | None = None
        self.report_sent = False
        self.state_push_elapsed = 0.0
        self.state_push_interval = float(self.app.network_config["state_update_interval"])
        self.status_hint = ""
        self.completed = False
        if self.mode == "online":
            self._apply_online_opening()

    def _board_origin(self) -> tuple[int, int]:
        cell = int(self.app.game_config["cell_size"])
        board_w = self.board.width * cell
        board_h = self.board.height * cell
        top_panel = 140
        x = (self.app.screen.get_width() - board_w) // 2
        y = top_panel + (self.app.screen.get_height() - top_panel - board_h) // 2
        return x, y

    def _board_rect(self) -> "pygame.Rect":
        cell = int(self.app.game_config["cell_size"])
        ox, oy = self._board_origin()
        return pygame.Rect(ox, oy, self.board.width * cell, self.board.height * cell)

    def handle_event(self, event: "pygame.event.Event") -> None:
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.result_state != "running":
            return
        if event.button not in (1, 3):
            return
        board_rect = self._board_rect()
        if not board_rect.collidepoint(event.pos):
            return
        cell_size = int(self.app.game_config["cell_size"])
        x = (event.pos[0] - board_rect.left) // cell_size
        y = (event.pos[1] - board_rect.top) // cell_size
        if event.button == 1:
            result = self.board.reveal(x, y)
            if result.newly_revealed:
                for cell in result.revealed_cells:
                    self.animations.add_reveal(cell)
            if result.hit_mine:
                self.animations.trigger_explosion((x, y))
                self.app.audio.play("explosion")
            else:
                self.app.audio.play("click")
        elif event.button == 3:
            if self.board.toggle_flag(x, y):
                self.app.audio.play("flag")

    def update(self, dt: float) -> None:
        self.animations.update(dt)

        if self.result_state == "running":
            self.elapsed += dt
            self.timer.update(dt)
            if self.board.is_loss:
                self.result_state = "loss"
            elif self.board.is_win:
                self.result_state = "win"
                self._auto_flag_mines()
                self.animations.trigger_pulse()
                self.app.audio.play("win")
            elif self.timer.is_expired:
                self.result_state = "timeout"

            if self.result_state in {"win", "loss", "timeout"}:
                if self.mode == "single":
                    if self.result_state == "loss" and self.animations.explosion.active:
                        return
                    if not self.completed:
                        self.completed = True
                        self._complete_singleplayer()
                    return
                self._submit_online_report()

        if self.mode == "online":
            self._process_online(dt)
            if self.result_state == "completed_online":
                self._complete_online()
            elif self.result_state == "disconnected":
                self._close_peer()
                self.switch(
                    _ui_scenes().GameOverScene(
                        self.app,
                        title="Онлайн матч",
                        lines=[
                            "Соединение потеряно.",
                            self.status_hint or "Связь с соперником прервана.",
                        ],
                    )
                )
        elif (
            self.mode == "single"
            and self.result_state == "loss"
            and not self.animations.explosion.active
            and not self.completed
        ):
            self.completed = True
            self._complete_singleplayer()

    def _build_report(self) -> dict[str, Any]:
        completion_time = self.elapsed if self.result_state == "win" else None
        status = self.result_state
        if status not in {"win", "loss", "timeout"}:
            status = "timeout"
        return {
            "type": "finish_report",
            "name": self.local_name,
            "status": status,
            "completion_time": completion_time,
            "score": self.current_score,
        }

    def _submit_online_report(self) -> None:
        if self.local_report is not None:
            return
        self.local_report = self._build_report()
        if self.peer is not None:
            self.peer.send(self.local_report)
            self.report_sent = True
        self.result_state = "awaiting_result"

    def _process_online(self, dt: float) -> None:
        if self.peer is None:
            self.result_state = "disconnected"
            self.status_hint = "Сетевое соединение отсутствует."
            return

        self.state_push_elapsed += dt
        if self.result_state == "running" and self.state_push_elapsed >= self.state_push_interval:
            payload = {
                "type": "state_update",
                "name": self.local_name,
                "revealed_safe": self.board.revealed_safe_count,
                "flags_used": self.board.flags_used,
                "time_left": self.timer.seconds_left_int,
                "score": self.current_score,
                "status": "running",
            }
            self.peer.send(payload)
            self.state_push_elapsed = 0.0

        for message in self.peer.poll():
            msg_type = message.get("type")
            if msg_type == "system":
                event = message.get("event")
                if event == "error":
                    if self.local_report is not None and self.remote_report is not None:
                        self.match_result = self._build_local_match_result()
                        self.result_state = "completed_online"
                    else:
                        self.result_state = "disconnected"
                        self.status_hint = message.get("message", "unknown network error")
                continue
            if msg_type == "hello":
                self.remote_name = message.get("name", self.remote_name or "Peer")
            elif msg_type == "state_update":
                self.remote_state = message
            elif msg_type == "finish_report":
                self.remote_report = message
                if self.role == "host" and self.local_report is not None:
                    self._host_resolve_result()
            elif msg_type == "match_result":
                self.match_result = message
                self.result_state = "completed_online"
            elif msg_type in {"disconnect", "error"}:
                if self.local_report is not None and self.remote_report is not None:
                    self.match_result = self._build_local_match_result()
                    self.result_state = "completed_online"
                else:
                    self.result_state = "disconnected"
                    self.status_hint = message.get("message", "remote disconnect")

        if self.role == "host" and self.result_state == "awaiting_result" and self.remote_report is not None:
            self._host_resolve_result()

    def _host_resolve_result(self) -> None:
        if self.local_report is None or self.remote_report is None or self.peer is None:
            return
        result = arbitrate_winner(
            host_report=self.local_report,
            client_report=self.remote_report,
            host_name=self.local_name,
            client_name=self.remote_report.get("name", self.remote_name or "Client"),
        )
        payload = {
            "type": "match_result",
            "winner": result["winner"],
            "winner_role": result.get("winner_role"),
            "reason": result["reason"],
            "host_name": self.local_name,
            "client_name": self.remote_report.get("name", self.remote_name or "Client"),
            "host_score": int(self.local_report.get("score", 0)),
            "client_score": int(self.remote_report.get("score", 0)),
        }
        self.peer.send(payload)
        self.match_result = payload
        self.result_state = "completed_online"

    def _build_local_match_result(self) -> dict[str, Any]:
        if self.local_report is None or self.remote_report is None:
            return {}
        if self.role == "host":
            host_report = self.local_report
            client_report = self.remote_report
            host_name = self.local_name
            client_name = self.remote_report.get("name", self.remote_name or "Client")
        else:
            host_report = self.remote_report
            client_report = self.local_report
            host_name = self.remote_report.get("name", self.remote_name or "Host")
            client_name = self.local_name
        result = arbitrate_winner(
            host_report=host_report,
            client_report=client_report,
            host_name=host_name,
            client_name=client_name,
        )
        return {
            "type": "match_result",
            "winner": result["winner"],
            "winner_role": result.get("winner_role"),
            "reason": result["reason"],
            "host_name": host_name,
            "client_name": client_name,
            "host_score": int(host_report.get("score", 0)),
            "client_score": int(client_report.get("score", 0)),
        }

    def _complete_online(self) -> None:
        if self.match_result is None:
            peer = self.peer
            self.peer = None
            self.switch(
                _ui_scenes().GameOverScene(
                    self.app,
                    title="Онлайн матч",
                    lines=["Матч завершён без результата.", "Нет данных от соперника."],
                    peer=peer,
                    close_after=0.5,
                )
            )
            return

        winner_role = self.match_result.get("winner_role")
        winner = self.match_result.get("winner")
        local_role = "host" if self.role == "host" else "client"
        if winner_role is None and winner is None:
            headline = "Ничья"
        elif winner_role is not None:
            if winner_role == local_role:
                headline = "Вы победили"
            else:
                winner_name = (
                    self.match_result.get("host_name", "HOST")
                    if winner_role == "host"
                    else self.match_result.get("client_name", "CLIENT")
                )
                headline = f"Победил: {winner_name}"
        elif winner == self.local_name:
            headline = "Вы победили"
        else:
            headline = f"Победил: {winner}"

        reason = self.match_result.get("reason", "")
        reason_map = {
            "faster_clear": "быстрее открыл поле",
            "score_tiebreak": "лучший счёт",
            "only_clear": "единственный очистил поле",
            "score_after_fail": "лучший счёт после ошибки",
            "score_after_timeout": "лучший счёт после тайм-аута",
            "timeout": "время вышло",
            "draw": "ничья",
        }
        reason_text = reason_map.get(reason, reason)

        lines = [
            f"Причина: {reason_text}",
            f"Ваш счёт: {self.current_score}",
        ]
        if self.remote_report is not None:
            lines.append(f"Счёт соперника: {int(self.remote_report.get('score', 0))}")
        close_after = 2.0 if self.role == "host" else 0.5
        peer = self.peer
        self.peer = None
        self.switch(
            _ui_scenes().GameOverScene(
                self.app,
                title=headline,
                lines=lines,
                peer=peer,
                close_after=close_after,
            )
        )

    def _complete_singleplayer(self) -> None:
        score = self.current_score
        time_left = self.timer.seconds_left_int
        if self.result_state == "win" and self.app.leaderboard.is_new_top(score):
            cancel_scene = _ui_scenes().GameOverScene(
                self.app,
                title="Победа",
                lines=[f"Счёт: {score}", f"Осталось времени: {time_left} сек"],
            )
            self.switch(
                _ui_scenes().NameEntryScene(
                    app=self.app,
                    score=score,
                    difficulty=self.difficulty_key,
                    time_left=time_left,
                    cancel_scene=cancel_scene,
                )
            )
            return

        if self.result_state == "win":
            title = "Победа"
            lines = [f"Счёт: {score}", f"Осталось времени: {time_left} сек"]
        elif self.result_state == "timeout":
            title = "Время вышло"
            lines = [f"Счёт: {score}"]
        else:
            title = "Поражение"
            lines = [f"Счёт: {score}"]
        self.switch(_ui_scenes().GameOverScene(self.app, title=title, lines=lines))

    def _close_peer(self) -> None:
        if self.peer is not None:
            self.peer.close()
            self.peer = None

    def _auto_flag_mines(self) -> None:
        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.cell(x, y)
                if cell.is_mine and not cell.flagged:
                    cell.flagged = True

    def _apply_online_opening(self) -> None:
        cx = self.board.width // 2
        cy = self.board.height // 2
        if self.board.generated:
            return
        result = self.board.reveal(cx, cy)
        if result.newly_revealed:
            for cell in result.revealed_cells:
                self.animations.add_reveal(cell)

    @property
    def current_score(self) -> int:
        base = int(self.diff_cfg["difficulty_base"])
        return compute_score(
            difficulty_base=base,
            revealed_safe=self.board.revealed_safe_count,
            time_left=self.timer.seconds_left_int,
            wrong_flags=self.board.wrong_flags,
        )

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))

        title = f"Сапёр | {self.diff_cfg['label']} | seed={self.seed}"
        header = self.app.font(26, bold=True).render(title, True, tuple(colors["text"]))
        screen.blit(header, (40, 30))

        timer_text = f"Время: {_format_timer(self.timer.seconds_left_int)}"
        timer = self.app.font(24).render(timer_text, True, tuple(colors["text"]))
        screen.blit(timer, (40, 70))

        score_text = f"Счёт: {self.current_score}"
        score = self.app.font(24).render(score_text, True, tuple(colors["text"]))
        screen.blit(score, (40, 100))

        if self.mode == "online" and self.remote_state is not None:
            other = self.app.font(20).render(
                f"Соперник: {self.remote_name} | Очки: {self.remote_state.get('score', 0)}",
                True,
                tuple(colors["accent"]),
            )
            screen.blit(other, (40, 130))

        board_rect = self._board_rect()
        cell_size = int(self.app.game_config["cell_size"])
        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.cell(x, y)
                rx = board_rect.left + x * cell_size
                ry = board_rect.top + y * cell_size
                rect = pygame.Rect(rx, ry, cell_size, cell_size)
                reveal_anim = self.animations.reveal.get((x, y))

                if cell.revealed:
                    base_color = tuple(colors["mine_cell"] if cell.is_mine else colors["revealed_cell"])
                    if reveal_anim is not None:
                        progress = reveal_anim.progress
                        hidden = colors["hidden_cell"]
                        blended = (
                            int(hidden[0] + (base_color[0] - hidden[0]) * progress),
                            int(hidden[1] + (base_color[1] - hidden[1]) * progress),
                            int(hidden[2] + (base_color[2] - hidden[2]) * progress),
                        )
                        pygame.draw.rect(screen, blended, rect)
                    else:
                        pygame.draw.rect(screen, base_color, rect)

                    if cell.is_mine:
                        pygame.draw.circle(screen, (20, 20, 20), rect.center, cell_size // 4)
                    elif cell.adjacent_mines > 0:
                        color = self.NUMBER_COLORS.get(cell.adjacent_mines, (0, 0, 0))
                        label = self.app.font(max(18, cell_size // 2), bold=True).render(
                            str(cell.adjacent_mines),
                            True,
                            color,
                        )
                        label_rect = label.get_rect(center=rect.center)
                        screen.blit(label, label_rect)
                else:
                    pygame.draw.rect(screen, tuple(colors["hidden_cell"]), rect)
                    if cell.flagged:
                        pygame.draw.polygon(
                            screen,
                            tuple(colors["flag_cell"]),
                            [
                                (rect.left + cell_size // 3, rect.top + cell_size // 5),
                                (rect.left + cell_size // 3, rect.bottom - cell_size // 5),
                                (rect.right - cell_size // 5, rect.centery),
                            ],
                        )

                pygame.draw.rect(screen, tuple(colors["grid_line"]), rect, width=1)

        if self.animations.explosion.active:
            ex = self.animations.explosion
            cx, cy = ex.center
            center_px = (
                board_rect.left + cx * cell_size + cell_size // 2,
                board_rect.top + cy * cell_size + cell_size // 2,
            )
            radius = max(8, int(cell_size * 1.5 * ex.progress))
            pygame.draw.circle(screen, tuple(colors["danger"]), center_px, radius, width=3)

        if self.result_state == "awaiting_result":
            _draw_centered_text(
                screen,
                self.app.font(34, bold=True),
                "Ожидание результата соперника...",
                tuple(colors["text"]),
                130,
            )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import MinesweeperApp
