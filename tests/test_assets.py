"""Tests for the assets module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sit_stand_reminder.assets import get_asset_path, get_bundle_dir, load_image


class TestGetBundleDir:
    """Tests for get_bundle_dir."""

    def test_returns_absolute_path(self) -> None:
        path = get_bundle_dir()
        assert Path(path).is_absolute()
        assert Path(path).exists()


class TestGetAssetPath:
    """Tests for get_asset_path."""

    def test_finds_existing_image(self) -> None:
        path = get_asset_path("sit_down", "images", ".png")
        assert path is not None
        assert Path(path).exists()

    def test_finds_existing_audio(self) -> None:
        path = get_asset_path("sit", "audio", ".wav")
        assert path is not None
        assert Path(path).exists()

    def test_returns_none_for_missing(self) -> None:
        path = get_asset_path("nonexistent", "images", ".png")
        assert path is None


class TestLoadImage:
    """Tests for load_image."""

    def test_loads_existing_image(self) -> None:
        img = load_image("sit_down", (100, 100))
        assert img is not None
        assert img.size == (100, 100)

    def test_caches_result(self) -> None:
        img1 = load_image("sit_down", (50, 50))
        img2 = load_image("sit_down", (50, 50))
        assert img1 is img2

    def test_returns_none_for_missing(self) -> None:
        img = load_image("nonexistent", (100, 100))
        assert img is None
