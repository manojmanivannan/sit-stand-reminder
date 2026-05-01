"""Tests for the config module."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from sit_stand_reminder.config import AppConfig, _config_dir, _config_file, load_config, save_config


class TestAppConfig:
    """Tests for the AppConfig dataclass."""

    def test_default_values(self) -> None:
        config = AppConfig()
        assert config.sit_for == 20
        assert config.stand_for == 8
        assert config.walk_for == 2
        assert config.theme == "auto"
        assert config.mute is False
        assert config.auto_close_delay == 60
        assert config.counters == {
            "SIT DOWN": {"completed": 0, "ignored": 0},
            "STAND UP": {"completed": 0, "ignored": 0},
            "WALK": {"completed": 0, "ignored": 0},
        }

    def test_validate_valid(self) -> None:
        config = AppConfig(sit_for=15, stand_for=10, walk_for=5)
        assert config.validate() is None

    def test_validate_invalid_sum(self) -> None:
        config = AppConfig(sit_for=10, stand_for=10, walk_for=15)
        error = config.validate()
        assert error is not None
        assert "35" in error

    def test_validate_too_small(self) -> None:
        config = AppConfig(sit_for=0, stand_for=15, walk_for=15)
        error = config.validate()
        assert error is not None
        assert "at least 1" in error

    def test_copy(self) -> None:
        original = AppConfig()
        modified = original.copy(sit_for=25, theme="dark")
        assert modified.sit_for == 25
        assert modified.theme == "dark"
        # Original unchanged
        assert original.sit_for == 20
        assert original.theme == "auto"


class TestConfigPersistence:
    """Tests for load_config and save_config."""

    def test_load_missing_file_returns_defaults(self, tmp_path: Path) -> None:
        with patch("sit_stand_reminder.config._config_dir", return_value=tmp_path):
            config = load_config()
        assert config.sit_for == 20
        assert config.theme == "auto"

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        config = AppConfig(sit_for=15, stand_for=10, walk_for=5, theme="dark", mute=True)
        with patch("sit_stand_reminder.config._config_dir", return_value=tmp_path):
            save_config(config)
            loaded = load_config()
        assert loaded.sit_for == 15
        assert loaded.stand_for == 10
        assert loaded.walk_for == 5
        assert loaded.theme == "dark"
        assert loaded.mute is True

    def test_load_malformed_file_returns_defaults(self, tmp_path: Path) -> None:
        (tmp_path / "config.json").write_text("not json")
        with patch("sit_stand_reminder.config._config_dir", return_value=tmp_path):
            config = load_config()
        assert config.sit_for == 20

    def test_config_dir_creates_directory(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "sit-stand-reminder"
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmp_path / "a" / "b")}, clear=False):
            with patch("platform.system", return_value="Linux"):
                result = _config_dir()
        assert result.exists()


class TestConfigFilePath:
    """Tests for the private path helper."""

    def test_config_file_returns_json(self, tmp_path: Path) -> None:
        with patch("sit_stand_reminder.config._config_dir", return_value=tmp_path):
            path = _config_file()
        assert path.name == "config.json"
        assert path.parent == tmp_path
