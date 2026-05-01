"""Cross-platform audio playback."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Callable


def _get_player() -> Callable[[str], None]:
    """Return the platform-specific audio playback function."""
    system = platform.system()
    if system == "Windows":
        import winsound
        return lambda path: winsound.PlaySound(path, winsound.SND_FILENAME)
    if system == "Darwin":
        return lambda path: subprocess.run(
            ["afplay", path], capture_output=True, timeout=10
        )
    # Linux and others
    def _linux_player(path: str) -> None:
        if shutil.which("paplay"):
            subprocess.run(["paplay", path], capture_output=True, timeout=10)
        elif shutil.which("aplay"):
            subprocess.run(["aplay", path], capture_output=True, timeout=10)
    return _linux_player


try:
    _PLATFORM_PLAYER = _get_player()
except Exception:
    _PLATFORM_PLAYER = None


def _audio_filename(phase_name: str) -> str:
    """Map phase name to audio file name."""
    mapping = {
        "SIT DOWN": "sit",
        "STAND UP": "stand",
        "WALK": "walk",
    }
    return mapping.get(phase_name, phase_name.lower().replace(" ", "_"))


def play_audio(phase_name: str, *, muted: bool = False) -> None:
    """Play the audio alert for a phase if not muted."""
    if muted or _PLATFORM_PLAYER is None:
        return
    try:
        bundle = Path(__file__).parent.parent
        filename = _audio_filename(phase_name)
        path = bundle / "audio" / f"{filename}.wav"
        if path.exists():
            _PLATFORM_PLAYER(str(path))
    except Exception:
        pass  # Audio is non-critical
