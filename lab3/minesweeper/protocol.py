from __future__ import annotations

import json
from typing import Any


ALLOWED_MESSAGE_TYPES = {
    "hello",
    "match_config",
    "state_update",
    "finish_report",
    "match_result",
    "error",
    "disconnect",
}


def validate_message(message: dict[str, Any]) -> None:
    if "type" not in message:
        raise ValueError("Network message requires 'type'.")
    message_type = message["type"]
    if message_type not in ALLOWED_MESSAGE_TYPES:
        raise ValueError(f"Unsupported message type: {message_type}")


def encode_message(message: dict[str, Any]) -> bytes:
    validate_message(message)
    serialized = json.dumps(message, ensure_ascii=False)
    return (serialized + "\n").encode("utf-8")


def decode_buffer(buffer: bytes) -> tuple[list[dict[str, Any]], bytes]:
    lines = buffer.split(b"\n")
    tail = lines[-1]
    messages: list[dict[str, Any]] = []
    for line in lines[:-1]:
        if not line.strip():
            continue
        decoded = json.loads(line.decode("utf-8"))
        if isinstance(decoded, dict):
            validate_message(decoded)
            messages.append(decoded)
    return messages, tail


def arbitrate_winner(
    host_report: dict[str, Any],
    client_report: dict[str, Any],
    host_name: str,
    client_name: str,
) -> dict[str, Any]:
    host_status = host_report.get("status")
    client_status = client_report.get("status")
    host_time = host_report.get("completion_time")
    client_time = client_report.get("completion_time")
    host_score = int(host_report.get("score", 0))
    client_score = int(client_report.get("score", 0))

    if host_status == "win" and client_status == "win":
        if host_time is not None and client_time is not None:
            if host_time < client_time:
                return {"winner": host_name, "winner_role": "host", "reason": "faster_clear"}
            if client_time < host_time:
                return {"winner": client_name, "winner_role": "client", "reason": "faster_clear"}
        if host_score > client_score:
            return {"winner": host_name, "winner_role": "host", "reason": "score_tiebreak"}
        if client_score > host_score:
            return {"winner": client_name, "winner_role": "client", "reason": "score_tiebreak"}
        return {"winner": None, "winner_role": None, "reason": "draw"}

    if host_status == "win":
        return {"winner": host_name, "winner_role": "host", "reason": "only_clear"}
    if client_status == "win":
        return {"winner": client_name, "winner_role": "client", "reason": "only_clear"}

    if host_status == "timeout" and client_status == "timeout":
        if host_score > client_score:
            return {"winner": host_name, "winner_role": "host", "reason": "score_after_timeout"}
        if client_score > host_score:
            return {"winner": client_name, "winner_role": "client", "reason": "score_after_timeout"}
        return {"winner": None, "winner_role": None, "reason": "draw"}

    if host_status == "timeout" and client_status == "loss":
        return {"winner": client_name, "winner_role": "client", "reason": "timeout"}
    if client_status == "timeout" and host_status == "loss":
        return {"winner": host_name, "winner_role": "host", "reason": "timeout"}

    if host_score > client_score:
        return {"winner": host_name, "winner_role": "host", "reason": "score_after_fail"}
    if client_score > host_score:
        return {"winner": client_name, "winner_role": "client", "reason": "score_after_fail"}
    return {"winner": None, "winner_role": None, "reason": "draw"}
