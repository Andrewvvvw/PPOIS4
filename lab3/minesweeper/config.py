from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_GAME_GROUPS = {
    "window",
    "fps",
    "difficulties",
    "timed_mode",
    "scoring",
    "animations",
    "audio",
}


class ConfigError(ValueError):
    """Raised when a config file is missing required data."""


@dataclass(slots=True, frozen=True)
class Paths:
    root: Path
    config_dir: Path
    data_dir: Path
    assets_dir: Path


def project_paths() -> Paths:
    root = Path(__file__).resolve().parents[1]
    return Paths(
        root=root,
        config_dir=root / "config",
        data_dir=root / "data",
        assets_dir=root / "assets",
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Config root must be an object: {path}")
    return data


def load_game_config() -> dict[str, Any]:
    paths = project_paths()
    config = load_json(paths.config_dir / "game_config.json")
    missing = REQUIRED_GAME_GROUPS.difference(config.keys())
    if missing:
        raise ConfigError(f"Missing required config groups: {', '.join(sorted(missing))}")
    if not config["difficulties"]:
        raise ConfigError("At least one difficulty must be configured.")
    return config


def load_network_config() -> dict[str, Any]:
    paths = project_paths()
    config = load_json(paths.config_dir / "network_config.json")
    for key in ("host", "port", "connect_timeout", "read_timeout", "state_update_interval"):
        if key not in config:
            raise ConfigError(f"Missing network config key: {key}")
    return config


def records_path() -> Path:
    return project_paths().data_dir / "records.json"


def asset_path(relative_path: str) -> Path:
    return project_paths().root / relative_path

