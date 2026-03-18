from __future__ import annotations

import pygame
import pygame_gui

import random
import socket

from typing import Any

from .game_scene import BaseScene, GameScene
from .network import NetworkOptions, NetworkPeer


def _centered_rect(screen: "pygame.Surface", width: int, height: int, y: int) -> "pygame.Rect":
    x = (screen.get_width() - width) // 2
    return pygame.Rect(x, y, width, height)


class MenuScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 400, 50, 80),
            text="Сапёр",
            manager=self.ui_manager,
        )
        btn_w, btn_h, gap = 320, 50, 14
        start_y = 200
        self.start_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y),
            text="Начать игру",
            manager=self.ui_manager,
        )
        self.records_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + (btn_h + gap)),
            text="Таблица рекордов",
            manager=self.ui_manager,
        )
        self.help_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + 2 * (btn_h + gap)),
            text="Справка",
            manager=self.ui_manager,
        )
        self.exit_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + 3 * (btn_h + gap)),
            text="Выход",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_btn:
                self.switch(StartGameScene(self.app))
            elif event.ui_element == self.records_btn:
                self.switch(RecordsScene(self.app))
            elif event.ui_element == self.help_btn:
                self.switch(HelpScene(self.app))
            elif event.ui_element == self.exit_btn:
                self.should_quit = True

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class StartGameScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 420, 50, 90),
            text="Режим игры",
            manager=self.ui_manager,
        )
        btn_w, btn_h, gap = 300, 50, 14
        start_y = 220
        self.single_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y),
            text="Одиночная игра",
            manager=self.ui_manager,
        )
        self.online_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + btn_h + gap),
            text="Онлайн игра",
            manager=self.ui_manager,
        )
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + 2 * (btn_h + gap)),
            text="Назад",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.single_btn:
                self.switch(SingleplayerSetupScene(self.app))
            elif event.ui_element == self.online_btn:
                self.switch(OnlineSetupScene(self.app))
            elif event.ui_element == self.back_btn:
                self.switch(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class SingleplayerSetupScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 420, 50, 90),
            text="Сложность",
            manager=self.ui_manager,
        )
        self.diff_keys = list(self.app.game_config["difficulties"].keys())
        btn_w, btn_h, gap = 380, 50, 14
        start_y = 200
        self.diff_buttons: list[pygame_gui.elements.UIButton] = []
        for idx, key in enumerate(self.diff_keys):
            label = self.app.game_config["difficulties"][key]["label"]
            btn = pygame_gui.elements.UIButton(
                relative_rect=_centered_rect(screen, btn_w, btn_h, start_y + idx * (btn_h + gap)),
                text=label,
                manager=self.ui_manager,
            )
            self.diff_buttons.append(btn)
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 220, 46, start_y + len(self.diff_keys) * (btn_h + gap) + 10),
            text="Назад",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_btn:
                self.switch(StartGameScene(self.app))
                return
            for idx, btn in enumerate(self.diff_buttons):
                if event.ui_element == btn:
                    key = self.diff_keys[idx]
                    self.switch(GameScene(self.app, mode="single", difficulty_key=key))
                    return

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class OnlineSetupScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.mode = "host"
        self.diff_keys = list(self.app.game_config["difficulties"].keys())
        self.diff_idx = 0
        self.error = ""

        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 500, 50, 40),
            text="Онлайн настройка",
            manager=self.ui_manager,
        )

        self.host_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(360, 120, 120, 40),
            text="HOST",
            manager=self.ui_manager,
        )
        self.join_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(500, 120, 120, 40),
            text="JOIN",
            manager=self.ui_manager,
        )

        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(260, 190, 150, 30),
            text="Имя:",
            manager=self.ui_manager,
        )
        self.name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(420, 185, 380, 35),
            manager=self.ui_manager,
        )
        self.name_entry.set_text("Player")

        self.ip_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(260, 240, 150, 30),
            text="IP сервера:",
            manager=self.ui_manager,
        )
        self.ip_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(420, 235, 380, 35),
            manager=self.ui_manager,
        )
        self.ip_entry.set_text("127.0.0.1")

        self.port_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(260, 290, 150, 30),
            text="Порт:",
            manager=self.ui_manager,
        )
        self.port_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(420, 285, 200, 35),
            manager=self.ui_manager,
        )
        self.port_entry.set_text(str(self.app.network_config["port"]))

        self.diff_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(260, 340, 150, 30),
            text="Сложность:",
            manager=self.ui_manager,
        )
        self.diff_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, 335, 380, 35),
            text=self.app.game_config["difficulties"][self.diff_keys[self.diff_idx]]["label"],
            manager=self.ui_manager,
        )

        self.start_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 220, 46, 420),
            text="Старт",
            manager=self.ui_manager,
        )
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 220, 46, 480),
            text="Назад",
            manager=self.ui_manager,
        )

        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 640, 30, 540),
            text="",
            manager=self.ui_manager,
        )

        self._apply_mode()

    def _apply_mode(self) -> None:
        if self.mode == "host":
            self.ip_entry.enable()
            self.diff_btn.show()
            self.diff_label.show()
        else:
            self.ip_entry.enable()
            self.diff_btn.hide()
            self.diff_label.hide()

    def _start_online(self) -> None:
        self.error = ""
        name = self.name_entry.get_text().strip() or "Player"
        try:
            port = int(self.port_entry.get_text())
        except ValueError:
            self.error = "Некорректный порт"
            self.error_label.set_text(self.error)
            return
        if port <= 0 or port > 65535:
            self.error = "Некорректный порт"
            self.error_label.set_text(self.error)
            return

        host = str(self.app.network_config.get("host", "0.0.0.0"))
        join_ip = self.ip_entry.get_text().strip() or "127.0.0.1"
        try:
            import ipaddress

            if self.mode == "join":
                ipaddress.ip_address(join_ip)
                host = join_ip
            else:
                host_ip = self.ip_entry.get_text().strip()
                if host_ip:
                    ipaddress.ip_address(host_ip)
                    host = host_ip
        except ValueError:
            self.error = "Некорректный IP"
            self.error_label.set_text(self.error)
            return

        options = NetworkOptions(
            host=host,
            port=port,
            connect_timeout=float(self.app.network_config["connect_timeout"]),
            read_timeout=float(self.app.network_config["read_timeout"]),
        )
        try:
            peer = NetworkPeer(role=self.mode, options=options, username=name)
            peer.start()
        except OSError as exc:
            self.error = f"Сетевая ошибка: {exc}"
            self.error_label.set_text(self.error)
            return

        diff_key = self.diff_keys[self.diff_idx]
        self.switch(
            OnlineWaitingScene(
                app=self.app,
                peer=peer,
                role=self.mode,
                local_name=name,
                difficulty_key=diff_key,
                join_ip=join_ip,
                port=port,
            )
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.host_btn:
                self.mode = "host"
                self._apply_mode()
            elif event.ui_element == self.join_btn:
                self.mode = "join"
                self._apply_mode()
            elif event.ui_element == self.diff_btn:
                self.diff_idx = (self.diff_idx + 1) % len(self.diff_keys)
                label = self.app.game_config["difficulties"][self.diff_keys[self.diff_idx]]["label"]
                self.diff_btn.set_text(label)
            elif event.ui_element == self.start_btn:
                self._start_online()
            elif event.ui_element == self.back_btn:
                self.switch(StartGameScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class OnlineWaitingScene(BaseScene):
    def __init__(
        self,
        app: "MinesweeperApp",
        peer: NetworkPeer,
        role: str,
        local_name: str,
        difficulty_key: str,
        join_ip: str,
        port: int,
    ):
        super().__init__(app)
        self.peer = peer
        self.role = role
        self.local_name = local_name
        self.remote_name = ""
        self.difficulty_key = difficulty_key
        self.join_ip = join_ip
        self.port = port
        self.seed = random.SystemRandom().randrange(1, 2**31 - 1)
        self.time_limit = int(self.app.game_config["difficulties"][difficulty_key]["time_limit"])
        self.match_config_received = role == "host"
        self.started = False
        self.error = ""

        screen = self.app.screen
        title_text = "Ожидание подключения..." if self.role == "host" else "Ожидание данных матча..."
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 700, 40, 80),
            text=title_text,
            manager=self.ui_manager,
        )
        self.info = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 800, 30, 140),
            text="",
            manager=self.ui_manager,
        )
        self.connection = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 800, 30, 180),
            text="",
            manager=self.ui_manager,
        )
        self.opponent = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 800, 30, 220),
            text="",
            manager=self.ui_manager,
        )
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 200, 46, 520),
            text="Назад",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_btn:
                self.peer.close()
                self.switch(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)
        events = self.peer.poll()
        for message in events:
            msg_type = message.get("type")
            if msg_type == "system":
                event = message.get("event")
                if event == "error":
                    self.error = message.get("message", "network error")
                continue
            if msg_type == "hello":
                self.remote_name = message.get("name", "Peer")
                if self.role == "host":
                    payload = {
                        "type": "match_config",
                        "difficulty": self.difficulty_key,
                        "seed": self.seed,
                        "time_limit": self.time_limit,
                    }
                    self.peer.send(payload)
            elif msg_type == "match_config" and self.role == "join":
                self.difficulty_key = message.get("difficulty", self.difficulty_key)
                self.seed = int(message.get("seed", self.seed))
                self.time_limit = int(message.get("time_limit", self.time_limit))
                self.match_config_received = True
            elif msg_type in {"disconnect", "error"}:
                self.error = message.get("message", "connection closed")

        if self.error:
            self.peer.close()
            self.switch(
                GameOverScene(
                    self.app,
                    title="Онлайн ошибка",
                    lines=["Соединение потеряно.", self.error],
                )
            )
            return

        if self.role == "join" and self.match_config_received and self.remote_name:
            self._start_game()
        if self.role == "host" and self.remote_name:
            self._start_game()

        self.info.set_text(f"Роль: {self.role.upper()} | Имя: {self.local_name}")
        if self.role == "host":
            self.connection.set_text(f"Подключение: {_resolve_local_ip()}:{self.port}")
        else:
            self.connection.set_text(f"Подключение: {self.join_ip}:{self.port}")
        if self.remote_name:
            self.opponent.set_text(f"Оппонент: {self.remote_name}")

    def _start_game(self) -> None:
        if self.started:
            return
        self.started = True
        self.switch(
            GameScene(
                app=self.app,
                mode="online",
                difficulty_key=self.difficulty_key,
                seed=self.seed,
                time_limit_override=self.time_limit,
                peer=self.peer,
                role=self.role,
                local_name=self.local_name,
                remote_name=self.remote_name or "Peer",
            )
        )

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class RecordsScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 500, 40, 60),
            text="Таблица рекордов",
            manager=self.ui_manager,
        )
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 200, 46, 540),
            text="Назад",
            manager=self.ui_manager,
        )
        self.text_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect(140, 120, 1000, 380),
            manager=self.ui_manager,
        )
        self._refresh_text()

    def _refresh_text(self) -> None:
        records = self.app.leaderboard.records
        if not records:
            html = "<b>Рекордов пока нет</b>"
        else:
            lines = ["<b>№ Имя Счёт Сложность Время</b>"]
            for idx, record in enumerate(records, start=1):
                lines.append(
                    f"{idx}. {record.name} — {record.score} — {record.difficulty} — {record.time_left}s"
                )
            html = "<br>".join(lines)
        self.text_box.set_text(html)

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_btn:
                self.switch(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class HelpScene(BaseScene):
    def __init__(self, app: "MinesweeperApp"):
        super().__init__(app)
        screen = self.app.screen
        self.title = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 400, 40, 60),
            text="Справка",
            manager=self.ui_manager,
        )
        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=_centered_rect(screen, 200, 46, 540),
            text="Назад",
            manager=self.ui_manager,
        )
        lines = self.app.game_config.get("help", [])
        html = "<br>".join(lines) if lines else "Нет данных"
        self.text_box = pygame_gui.elements.UITextBox(
            html_text=html,
            relative_rect=pygame.Rect(140, 120, 1000, 380),
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_btn:
                self.switch(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)


class GameOverScene(BaseScene):
    def __init__(self, app: "MinesweeperApp", title: str, lines: list[str], peer: NetworkPeer | None = None, close_after: float = 0.0):
        super().__init__(app)
        self.peer = peer
        self.close_after = max(0.0, float(close_after))
        self.close_timer = 0.0

        screen = self.app.screen
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 600, 40, 80),
            text=title,
            manager=self.ui_manager,
        )
        html = "<br>".join(lines) if lines else ""
        self.text_box = pygame_gui.elements.UITextBox(
            html_text=html,
            relative_rect=pygame.Rect(200, 140, 880, 200),
            manager=self.ui_manager,
        )
        self.menu_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(360, 400, 200, 46),
            text="Меню",
            manager=self.ui_manager,
        )
        self.records_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(600, 400, 200, 46),
            text="Рекорды",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.menu_btn:
                self._close_peer_now()
                self.switch(MenuScene(self.app))
            elif event.ui_element == self.records_btn:
                self._close_peer_now()
                self.switch(RecordsScene(self.app))

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)
        if self.peer is None:
            return
        if self.close_after <= 0.0:
            self._close_peer_now()
            return
        self.close_timer += dt
        if self.close_timer >= self.close_after:
            self._close_peer_now()

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)

    def _close_peer_now(self) -> None:
        if self.peer is None:
            return
        try:
            self.peer.close()
        finally:
            self.peer = None


class NameEntryScene(BaseScene):
    def __init__(self, app: "MinesweeperApp", score: int, difficulty: str, time_left: int, cancel_scene: BaseScene):
        super().__init__(app)
        self.score = score
        self.difficulty = difficulty
        self.time_left = time_left
        self.cancel_scene = cancel_scene

        screen = self.app.screen
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 600, 40, 80),
            text="Новый рекорд",
            manager=self.ui_manager,
        )
        info = f"Счёт: {score} | Осталось времени: {time_left} сек"
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=_centered_rect(screen, 800, 30, 140),
            text=info,
            manager=self.ui_manager,
        )
        self.name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=_centered_rect(screen, 360, 36, 210),
            manager=self.ui_manager,
        )
        self.save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, 280, 180, 46),
            text="Сохранить",
            manager=self.ui_manager,
        )
        self.cancel_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(620, 280, 180, 46),
            text="Отмена",
            manager=self.ui_manager,
        )

    def handle_event(self, event: "pygame.event.Event") -> None:
        self.ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.save_btn:
                self._save()
            elif event.ui_element == self.cancel_btn:
                self.switch(self.cancel_scene)

    def update(self, dt: float) -> None:
        self.ui_manager.update(dt)

    def render(self, screen: "pygame.Surface") -> None:
        colors = self.app.game_config["colors"]
        screen.fill(tuple(colors["background"]))
        self.ui_manager.draw_ui(screen)

    def _save(self) -> None:
        name = self.name_entry.get_text().strip() or "Player"
        self.app.leaderboard.add_record(
            name=name,
            score=self.score,
            difficulty=self.difficulty,
            time_left=self.time_left,
        )
        self.switch(RecordsScene(self.app))


def _resolve_local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import MinesweeperApp
