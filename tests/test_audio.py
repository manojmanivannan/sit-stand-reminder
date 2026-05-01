"""Tests for the audio module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sit_stand_reminder.audio import _audio_filename, play_audio


class TestAudioFilename:
    """Tests for the internal filename mapper."""

    def test_maps_phase_names(self) -> None:
        assert _audio_filename("SIT DOWN") == "sit"
        assert _audio_filename("STAND UP") == "stand"
        assert _audio_filename("WALK") == "walk"

    def test_falls_back_to_slug(self) -> None:
        assert _audio_filename("UNKNOWN PHASE") == "unknown_phase"


class TestPlayAudio:
    """Tests for play_audio."""

    def test_muted_does_nothing(self) -> None:
        # Should not crash when muted
        play_audio("SIT DOWN", muted=True)

    def test_no_player_does_nothing(self) -> None:
        with patch("sit_stand_reminder.audio._PLATFORM_PLAYER", None):
            play_audio("SIT DOWN", muted=False)

    def test_player_called_for_valid_file(self) -> None:
        mock_player = MagicMock()
        with patch("sit_stand_reminder.audio._PLATFORM_PLAYER", mock_player):
            play_audio("SIT DOWN", muted=False)
        mock_player.assert_called_once()

    def test_player_failure_is_silent(self) -> None:
        mock_player = MagicMock(side_effect=RuntimeError("boom"))
        with patch("sit_stand_reminder.audio._PLATFORM_PLAYER", mock_player):
            play_audio("SIT DOWN", muted=False)
