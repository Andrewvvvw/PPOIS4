from __future__ import annotations

from dataclasses import dataclass
import queue
import socket
import threading
from typing import Any

from .protocol import decode_buffer, encode_message


@dataclass(slots=True, frozen=True)
class NetworkOptions:
    host: str
    port: int
    connect_timeout: float
    read_timeout: float


class NetworkPeer:
    def __init__(self, role: str, options: NetworkOptions, username: str):
        if role not in {"host", "join"}:
            raise ValueError("role must be 'host' or 'join'")
        self.role = role
        self.options = options
        self.username = username
        self._running = False
        self._connected = False
        self._event_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._send_lock = threading.Lock()
        self._server_socket: socket.socket | None = None
        self._socket: socket.socket | None = None
        self._reader_thread: threading.Thread | None = None
        self._accept_thread: threading.Thread | None = None

    @property
    def connected(self) -> bool:
        return self._connected and self._socket is not None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        if self.role == "host":
            self._start_host()
        else:
            self._start_client()

    def _start_host(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.options.host, self.options.port))
        server.listen(1)
        server.settimeout(0.5)
        self._server_socket = server
        self._event_queue.put(
            {
                "type": "system",
                "event": "listening",
                "host": self.options.host,
                "port": self.options.port,
            }
        )
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def _accept_loop(self) -> None:
        assert self._server_socket is not None
        while self._running and not self._connected:
            try:
                client_socket, address = self._server_socket.accept()
            except socket.timeout:
                continue
            except OSError as exc:
                self._event_queue.put({"type": "system", "event": "error", "message": str(exc)})
                return
            client_socket.settimeout(self.options.read_timeout)
            self._socket = client_socket
            self._connected = True
            self._event_queue.put({"type": "system", "event": "connected", "address": address[0]})
            self.send({"type": "hello", "name": self.username})
            self._start_reader()
            return

    def _start_client(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.options.connect_timeout)
        try:
            sock.connect((self.options.host, self.options.port))
        except OSError:
            sock.close()
            self._running = False
            raise
        sock.settimeout(self.options.read_timeout)
        self._socket = sock
        self._connected = True
        self._event_queue.put({"type": "system", "event": "connected", "address": self.options.host})
        self.send({"type": "hello", "name": self.username})
        self._start_reader()

    def _start_reader(self) -> None:
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _reader_loop(self) -> None:
        buffer = b""
        while self._running and self._socket is not None:
            try:
                chunk = self._socket.recv(4096)
                if not chunk:
                    raise ConnectionError("Remote peer disconnected.")
                buffer += chunk
                messages, buffer = decode_buffer(buffer)
                for message in messages:
                    self._event_queue.put(message)
            except socket.timeout:
                continue
            except Exception as exc:  # noqa: BLE001
                self._event_queue.put({"type": "system", "event": "error", "message": str(exc)})
                self._running = False
                self._connected = False
                return

    def send(self, message: dict[str, Any]) -> bool:
        if self._socket is None:
            return False
        payload = encode_message(message)
        with self._send_lock:
            try:
                self._socket.sendall(payload)
                return True
            except OSError as exc:
                self._event_queue.put({"type": "system", "event": "error", "message": str(exc)})
                self._connected = False
                return False

    def poll(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        while True:
            try:
                events.append(self._event_queue.get_nowait())
            except queue.Empty:
                break
        return events

    def close(self) -> None:
        self._running = False
        if self._socket is not None:
            try:
                self.send({"type": "disconnect", "name": self.username})
            except Exception:  # noqa: BLE001
                pass
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None
        self._connected = False

