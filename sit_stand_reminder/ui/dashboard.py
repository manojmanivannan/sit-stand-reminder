"""Persistent dashboard window."""

from __future__ import annotations

import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from sit_stand_reminder.config import AppConfig
from sit_stand_reminder.scheduler import Phase
from sit_stand_reminder.ui.style import phase_bootstyle, phase_label


class DashboardWindow:
    """Small persistent window showing current phase, countdown, and controls."""

    def __init__(
        self,
        master: tk.Tk,
        config: AppConfig,
        on_settings: callable,
        on_quit: callable,
        on_toggle_mute: callable,
        on_test_reminder: callable | None = None,
    ):
        self.master = master
        self.config = config
        self.on_settings = on_settings
        self.on_quit = on_quit
        self.on_toggle_mute = on_toggle_mute
        self.on_test_reminder = on_test_reminder
        self._on_top_var = tk.BooleanVar(value=False)

        self._setup_window()
        self._build_ui()

    def _setup_window(self) -> None:
        self.window = tk.Toplevel(self.master)
        self.window.title("Sit-Stand Reminder")
        self.window.geometry("420x280")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=BOTH, expand=YES)

        # Phase badge
        self.phase_var = tk.StringVar(value="SIT DOWN")
        self.phase_label_widget = ttk.Label(
            container,
            textvariable=self.phase_var,
            font=("Helvetica", 22, "bold"),
            bootstyle="primary",
        )
        self.phase_label_widget.pack(pady=(0, 8))

        # Countdown
        self.countdown_var = tk.StringVar(value="20:00 until Stand")
        self.countdown_label = ttk.Label(
            container,
            textvariable=self.countdown_var,
            font=("Helvetica", 14),
        )
        self.countdown_label.pack(pady=(0, 12))

        # Counters row
        self.counters_var = tk.StringVar(value="")
        self.counters_label = ttk.Label(
            container,
            textvariable=self.counters_var,
            font=("Helvetica", 10),
            bootstyle="secondary",
        )
        self.counters_label.pack(pady=(0, 12))

        # Always on top toggle
        top_frame = ttk.Frame(container)
        top_frame.pack(fill=X, pady=(0, 8))
        ttk.Checkbutton(
            top_frame,
            text="Always on top",
            variable=self._on_top_var,
            command=self._toggle_on_top,
            bootstyle="secondary-round-toggle",
        ).pack(side=LEFT)

        # Controls
        controls = ttk.Frame(container)
        controls.pack(fill=X, pady=(8, 0))

        self.mute_btn = ttk.Button(
            controls,
            text="Mute",
            command=self._toggle_mute,
            bootstyle="secondary-outline",
            width=8,
        )
        self.mute_btn.pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            controls,
            text="Settings",
            command=self.on_settings,
            bootstyle="secondary-outline",
            width=8,
        ).pack(side=LEFT, padx=(0, 8))

        if self.on_test_reminder:
            ttk.Button(
                controls,
                text="Test",
                command=self.on_test_reminder,
                bootstyle="info-outline",
                width=8,
            ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            controls,
            text="Quit",
            command=self.on_quit,
            bootstyle="danger-outline",
            width=8,
        ).pack(side=RIGHT)

    def set_config(self, config: AppConfig) -> None:
        """Update the internal config reference (e.g. after settings save)."""
        self.config = config
        self.mute_btn.configure(text="Unmute" if self.config.mute else "Mute")

    def update_state(self, phase: Phase, seconds_left: int) -> None:
        """Refresh the dashboard with current phase and countdown."""
        if not self.window.winfo_exists():
            return
        self.phase_var.set(phase_label(phase))
        self.phase_label_widget.configure(bootstyle=phase_bootstyle(phase))

        mins, secs = divmod(seconds_left, 60)
        next_name = self._next_phase_name(phase)
        self.countdown_var.set(f"{mins:02d}:{secs:02d} until {next_name}")

        c = self.config.counters
        text = (
            f"Sit: {c['SIT DOWN']['completed']}/{c['SIT DOWN']['ignored']}   "
            f"Stand: {c['STAND UP']['completed']}/{c['STAND UP']['ignored']}   "
            f"Walk: {c['WALK']['completed']}/{c['WALK']['ignored']}"
        )
        self.counters_var.set(text)
        self.mute_btn.configure(text="Unmute" if self.config.mute else "Mute")

    def _next_phase_name(self, phase: Phase) -> str:
        mapping = {Phase.SIT: "Stand", Phase.STAND: "Walk", Phase.WALK: "Sit"}
        return mapping.get(phase, "Next")

    def _toggle_mute(self) -> None:
        self.config.mute = not self.config.mute
        self.mute_btn.configure(text="Unmute" if self.config.mute else "Mute")
        if self.on_toggle_mute:
            self.on_toggle_mute()

    def _toggle_on_top(self) -> None:
        self.window.attributes("-topmost", self._on_top_var.get())

    def _on_close(self) -> None:
        # Hide the window; the app continues running in the background.
        self.window.withdraw()

    def show(self) -> None:
        if not self.window.winfo_exists():
            return
        self.window.deiconify()
        self.window.lift()
