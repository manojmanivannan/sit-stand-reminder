"""Tests for the main application controller."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sit_stand_reminder.config import AppConfig
from sit_stand_reminder.main import App
from sit_stand_reminder.scheduler import Phase


class TestAppLogic:
    """Tests for App business logic (without Tk UI)."""

    def test_record_response_done(self) -> None:
        config = AppConfig()
        app = object.__new__(App)
        app.config = config
        app.dashboard = MagicMock()
        app.dashboard.window.winfo_exists.return_value = False

        app._record_response(Phase.SIT, "Done")
        assert config.counters["SIT DOWN"]["completed"] == 1
        assert config.counters["SIT DOWN"]["ignored"] == 0

    def test_record_response_skip(self) -> None:
        config = AppConfig()
        app = object.__new__(App)
        app.config = config
        app.dashboard = MagicMock()
        app.dashboard.window.winfo_exists.return_value = False

        app._record_response(Phase.STAND, "Skip")
        assert config.counters["STAND UP"]["completed"] == 0
        assert config.counters["STAND UP"]["ignored"] == 1

    def test_restart_scheduler_creates_new_instance(self) -> None:
        with patch("sit_stand_reminder.main.DashboardWindow", MagicMock()):
            with patch("sit_stand_reminder.main.Scheduler") as mock_scheduler_cls:
                # Return a fresh MagicMock each call so `is not` passes
                mock_scheduler_cls.side_effect = lambda *a, **k: MagicMock()
                with patch("sit_stand_reminder.main.setup_theme", return_value=MagicMock()):
                    with patch("sit_stand_reminder.main.load_config", return_value=AppConfig()):
                        with patch("tkinter.Tk"):
                            app = App()
                            old_scheduler = app.scheduler
                            app._restart_scheduler()
                            assert app.scheduler is not old_scheduler
                            mock_scheduler_cls.assert_called()
