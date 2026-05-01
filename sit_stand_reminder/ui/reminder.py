"""Reminder popup dialog."""

from __future__ import annotations

import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import ImageTk

from sit_stand_reminder.assets import load_image
from sit_stand_reminder.config import AppConfig
from sit_stand_reminder.scheduler import Phase
from sit_stand_reminder.ui.style import phase_bootstyle, phase_label


class ReminderDialog:
    """Modal reminder window with image, countdown, and action buttons."""

    def __init__(
        self,
        master: tk.Tk,
        config: AppConfig,
        phase: Phase,
        on_done: callable,
        on_skip: callable,
        on_settings: callable,
        on_mute_toggle: callable,
    ):
        self.master = master
        self.config = config
        self.phase = phase
        self.on_done = on_done
        self.on_skip = on_skip
        self.on_settings = on_settings
        self.on_mute_toggle = on_mute_toggle
        self._response: str | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._tick_job: str | None = None

        self._build()

    def _build(self) -> None:
        self.window = tk.Toplevel(self.master)
        self.window.title(phase_label(self.phase))
        self.window.geometry("500x680")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._skip)
        self._center_window(500, 680)

        # macOS: ensure the popup is actually visible and on top
        self.window.lift()
        self.window.focus_force()
        # Delay topmost so the window manager doesn't suppress it
        self.window.after(100, lambda: self.window.attributes("-topmost", True))

        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=BOTH, expand=YES)

        # Phase title
        title = ttk.Label(
            container,
            text=f"{phase_label(self.phase)} Reminder!",
            font=("Helvetica", 18, "bold"),
            bootstyle=phase_bootstyle(self.phase),
        )
        title.pack(pady=(0, 10))

        # Image
        self._load_image()
        if self._photo:
            img_label = ttk.Label(container, image=self._photo)
            img_label.pack(pady=(0, 10))
        else:
            ttk.Label(container, text="[Image not found]", bootstyle="secondary").pack(pady=(0, 10))

        # Auto-close progress
        self.time_left = self.config.auto_close_delay
        self.progress = ttk.Progressbar(
            container,
            maximum=self.config.auto_close_delay,
            mode="determinate",
            bootstyle=phase_bootstyle(self.phase),
            length=460,
        )
        self.progress.pack(pady=(0, 10))

        self.timer_label = ttk.Label(
            container,
            text=f"Auto-closing in {self.time_left}s",
            font=("Helvetica", 10),
            bootstyle="secondary",
        )
        self.timer_label.pack(pady=(0, 10))

        # Counters
        self.counters_var = tk.StringVar(value=self._counters_text())
        counters_label = ttk.Label(
            container,
            textvariable=self.counters_var,
            font=("Helvetica", 10),
            justify=LEFT,
            bootstyle="secondary",
        )
        counters_label.pack(pady=(0, 15))

        # Controls row
        controls = ttk.Frame(container)
        controls.pack(fill=X, pady=(10, 0))

        # Mute button
        self.mute_btn = ttk.Button(
            controls,
            text="Mute" if self.config.mute else "Unmute",
            command=self._toggle_mute,
            bootstyle="secondary-outline",
            width=10,
        )
        self.mute_btn.pack(side=LEFT, padx=(0, 8))

        # Done button (primary, default action)
        self.done_btn = ttk.Button(
            controls,
            text="Done",
            command=self._done,
            bootstyle=phase_bootstyle(self.phase),
            width=12,
        )
        self.done_btn.pack(side=LEFT, padx=(0, 8))

        # Skip button
        self.skip_btn = ttk.Button(
            controls,
            text="Skip",
            command=self._skip,
            bootstyle="secondary-outline",
            width=12,
        )
        self.skip_btn.pack(side=LEFT, padx=(0, 8))

        # Settings gear
        settings_btn = ttk.Button(
            controls,
            text="Settings",
            command=self._open_settings,
            bootstyle="secondary-outline",
            width=10,
        )
        settings_btn.pack(side=RIGHT)

        # Keyboard shortcuts
        self.window.bind("<Return>", lambda _e: self._done())
        self.window.bind("<Escape>", lambda _e: self._skip())
        self.window.bind("<m>", lambda _e: self._toggle_mute())
        self.window.bind("<s>", lambda _e: self._open_settings())

        # Start countdown after the window is fully mapped
        self._tick_job = self.window.after(1000, self._tick)

    def _load_image(self) -> None:
        name_map = {
            Phase.SIT: "sit_down",
            Phase.STAND: "stand_up",
            Phase.WALK: "walk",
        }
        name = name_map.get(self.phase, "sit_down")
        img = load_image(name, (250, 350))
        if img:
            self._photo = ImageTk.PhotoImage(img)

    def _counters_text(self) -> str:
        c = self.config.counters
        return (
            f"Sat down:      {c['SIT DOWN']['completed']}  (ignored {c['SIT DOWN']['ignored']})\n"
            f"Stood up:      {c['STAND UP']['completed']}  (ignored {c['STAND UP']['ignored']})\n"
            f"Walked:        {c['WALK']['completed']}  (ignored {c['WALK']['ignored']})"
        )

    def _center_window(self, width: int, height: int) -> None:
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _tick(self) -> None:
        if not self.window.winfo_exists():
            return
        if self._response is not None:
            return
        self.time_left -= 1
        self.progress["value"] = self.config.auto_close_delay - self.time_left
        self.timer_label.configure(text=f"Auto-closing in {self.time_left}s")
        if self.time_left <= 0:
            self._skip()
        else:
            self._tick_job = self.window.after(1000, self._tick)

    def _cancel_tick(self) -> None:
        if self._tick_job is not None:
            try:
                self.window.after_cancel(self._tick_job)
            except Exception:
                pass
            self._tick_job = None

    def _done(self) -> None:
        self._cancel_tick()
        self._response = "Done"
        if self.on_done:
            self.on_done()
        self.window.destroy()

    def _skip(self) -> None:
        self._cancel_tick()
        self._response = "Skip"
        if self.on_skip:
            self.on_skip()
        self.window.destroy()

    def _toggle_mute(self) -> None:
        self.config.mute = not self.config.mute
        text = "Unmute" if self.config.mute else "Mute"
        self.mute_btn.configure(text=text)
        if self.on_mute_toggle:
            self.on_mute_toggle()

    def _open_settings(self) -> None:
        if self.on_settings:
            self.on_settings()

    def wait(self) -> str | None:
        """Block until the dialog is closed, returning the user response."""
        self.window.wait_window()
        return self._response
