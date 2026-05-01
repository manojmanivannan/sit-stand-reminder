"""Theme setup and design tokens."""

from __future__ import annotations

import platform

import ttkbootstrap as ttk

from sit_stand_reminder.scheduler import Phase

_PHASE_BOOTSTYLE: dict[Phase, str] = {
    Phase.SIT: "primary",
    Phase.STAND: "success",
    Phase.WALK: "warning",
}

_PHASE_LABEL: dict[Phase, str] = {
    Phase.SIT: "SIT DOWN",
    Phase.STAND: "STAND UP",
    Phase.WALK: "WALK",
}

_THEME_MAP: dict[str, str] = {
    "light": "flatly",
    "dark": "darkly",
}


def resolve_theme(preference: str) -> str:
    """Map user preference to a ttkbootstrap theme name."""
    if preference in _THEME_MAP:
        return _THEME_MAP[preference]
    # Auto: default to light for now (system detection can be added later)
    return "flatly"


def phase_bootstyle(phase: Phase) -> str:
    """Return the ttkbootstrap bootstyle for a phase."""
    return _PHASE_BOOTSTYLE.get(phase, "secondary")


def phase_label(phase: Phase) -> str:
    """Return the human-readable label for a phase."""
    return _PHASE_LABEL.get(phase, "UNKNOWN")


def setup_theme(root, theme_name: str) -> ttk.Style:
    """Initialize ttkbootstrap theme on the given root window."""
    style = ttk.Style(theme=theme_name)
    return style
