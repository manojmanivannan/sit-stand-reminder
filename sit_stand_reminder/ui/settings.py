"""Settings dialog."""

from __future__ import annotations

import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from sit_stand_reminder.config import AppConfig
from sit_stand_reminder.ui.style import resolve_theme


class SettingsDialog:
    """Modal settings dialog with live validation and inline errors."""

    def __init__(
        self,
        master: tk.Tk,
        config: AppConfig,
        on_save: callable,
    ):
        self.master = master
        self.config = config
        self.on_save = on_save
        self._result: AppConfig | None = None

        self._build()

    def _build(self) -> None:
        self.window = tk.Toplevel(self.master)
        self.window.title("Reminder Settings")
        self.window.geometry("420x440")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
        self._center_window(420, 440)

        # Bring to front without grab_set (which breaks on macOS with withdrawn master)
        self.window.lift()
        self.window.focus_force()

        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=BOTH, expand=YES)

        # Cycle times
        ttk.Label(
            container,
            text="Cycle times (must sum to 30 minutes)",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor=W, pady=(0, 12))

        times_frame = ttk.Frame(container)
        times_frame.pack(fill=X, pady=(0, 8))

        self.sit_var = tk.IntVar(value=self.config.sit_for)
        self.stand_var = tk.IntVar(value=self.config.stand_for)
        self.walk_var = tk.IntVar(value=self.config.walk_for)

        self._spinbox_row(times_frame, "Sit:", self.sit_var, 0)
        self._spinbox_row(times_frame, "Stand:", self.stand_var, 1)
        self._spinbox_row(times_frame, "Walk:", self.walk_var, 2)

        # Error label
        self.error_var = tk.StringVar(value="")
        self.error_label = ttk.Label(
            container,
            textvariable=self.error_var,
            font=("Helvetica", 10),
            bootstyle="danger",
        )
        self.error_label.pack(fill=X, pady=(0, 12))

        # Theme
        ttk.Label(container, text="Theme:", font=("Helvetica", 11, "bold")).pack(anchor=W, pady=(0, 4))
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_frame = ttk.Frame(container)
        theme_frame.pack(fill=X, pady=(0, 12))
        for choice in ("auto", "light", "dark"):
            ttk.Radiobutton(
                theme_frame,
                text=choice.capitalize(),
                variable=self.theme_var,
                value=choice,
                bootstyle="secondary-toolbutton",
            ).pack(side=LEFT, padx=(0, 8))

        # Sound
        self.mute_var = tk.BooleanVar(value=self.config.mute)
        ttk.Checkbutton(
            container,
            text="Mute sound",
            variable=self.mute_var,
            bootstyle="secondary-round-toggle",
        ).pack(anchor=W, pady=(0, 8))

        # Auto-close delay
        ttk.Label(
            container,
            text="Auto-close delay (seconds):",
            font=("Helvetica", 11, "bold"),
        ).pack(anchor=W, pady=(0, 4))
        delay_frame = ttk.Frame(container)
        delay_frame.pack(fill=X, pady=(0, 12))
        self.delay_var = tk.IntVar(value=self.config.auto_close_delay)
        ttk.Scale(
            delay_frame,
            from_=15,
            to=120,
            variable=self.delay_var,
            orient=HORIZONTAL,
            length=300,
        ).pack(side=LEFT)
        self.delay_label = ttk.Label(
            delay_frame,
            text=str(self.config.auto_close_delay),
            width=4,
        )
        self.delay_label.pack(side=LEFT, padx=(8, 0))
        self.delay_var.trace_add("write", lambda *_: self.delay_label.configure(text=str(self.delay_var.get())))

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=(12, 0))

        self.save_btn = ttk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            bootstyle="primary",
            width=10,
        )
        self.save_btn.pack(side=RIGHT, padx=(8, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self._cancel,
            bootstyle="secondary-outline",
            width=10,
        ).pack(side=RIGHT)

        # Initial validation
        self._validate()

        # Bindings
        for var in (self.sit_var, self.stand_var, self.walk_var):
            var.trace_add("write", lambda *_: self._validate())

        self.window.bind("<Return>", lambda _e: self._save())
        self.window.bind("<Escape>", lambda _e: self._cancel())

    def _spinbox_row(self, parent: ttk.Frame, label: str, var: tk.IntVar, row: int) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=4)
        ttk.Label(frame, text=label, width=8).pack(side=LEFT)
        ttk.Spinbox(
            frame,
            from_=1,
            to=28,
            textvariable=var,
            width=8,
        ).pack(side=LEFT, padx=(8, 0))

    def _validate(self) -> None:
        try:
            total = self.sit_var.get() + self.stand_var.get() + self.walk_var.get()
        except tk.TclError:
            # Spinbox may contain non-numeric text temporarily
            self.error_var.set("Please enter valid numbers.")
            self.save_btn.configure(state=DISABLED)
            return

        if total != 30:
            self.error_var.set(f"Times must sum to 30 minutes (currently {total}).")
            self.save_btn.configure(state=DISABLED)
        elif any(v < 1 for v in (self.sit_var.get(), self.stand_var.get(), self.walk_var.get())):
            self.error_var.set("Each phase must be at least 1 minute.")
            self.save_btn.configure(state=DISABLED)
        else:
            self.error_var.set("")
            self.save_btn.configure(state=NORMAL)

    def _center_window(self, width: int, height: int) -> None:
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _save(self) -> None:
        if self.save_btn["state"] == DISABLED:
            return
        new_config = self.config.copy(
            sit_for=self.sit_var.get(),
            stand_for=self.stand_var.get(),
            walk_for=self.walk_var.get(),
            theme=self.theme_var.get(),
            mute=self.mute_var.get(),
            auto_close_delay=self.delay_var.get(),
        )
        self._result = new_config
        self.window.destroy()
        if self.on_save:
            self.on_save(new_config)

    def _cancel(self) -> None:
        self.window.destroy()

    def wait(self) -> AppConfig | None:
        """Block until the dialog closes, returning the new config or None."""
        self.window.wait_window()
        return self._result
