"""Configuration management with JSON persistence."""

from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppConfig:
    """Application configuration with sensible defaults."""

    sit_for: int = 20
    stand_for: int = 8
    walk_for: int = 2
    theme: str = "auto"  # "auto", "light", "dark"
    mute: bool = False
    auto_close_delay: int = 60  # seconds
    counters: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            "SIT DOWN": {"completed": 0, "ignored": 0},
            "STAND UP": {"completed": 0, "ignored": 0},
            "WALK": {"completed": 0, "ignored": 0},
        }
    )

    def validate(self) -> str | None:
        """Return error message if cycle times are invalid, else None."""
        total = self.sit_for + self.stand_for + self.walk_for
        if total != 30:
            return f"Cycle times must sum to 30 minutes (currently {total})."
        if any(v < 1 for v in (self.sit_for, self.stand_for, self.walk_for)):
            return "Each phase must be at least 1 minute."
        return None

    def copy(self, **changes: Any) -> "AppConfig":
        """Return a new AppConfig with the given fields updated."""
        data = asdict(self)
        data.update(changes)
        return AppConfig(**data)


def _config_dir() -> Path:
    """Return the platform-specific configuration directory."""
    system = platform.system()
    app_name = "sit-stand-reminder"
    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        # Linux / Unix
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _config_file() -> Path:
    return _config_dir() / "config.json"


def load_config() -> AppConfig:
    """Load configuration from disk or return defaults."""
    path = _config_file()
    if not path.exists():
        return AppConfig()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig(**data)
    except Exception:
        return AppConfig()


def save_config(config: AppConfig) -> None:
    """Save configuration to disk."""
    path = _config_file()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2)
