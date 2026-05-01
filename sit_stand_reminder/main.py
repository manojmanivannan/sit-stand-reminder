"""Application controller: lifecycle, threading, and UI coordination."""

from __future__ import annotations

import platform
import queue
import threading
import tkinter as tk

from sit_stand_reminder.audio import play_audio
from sit_stand_reminder.config import AppConfig, load_config, save_config
from sit_stand_reminder.scheduler import PHASE_NAMES, Cycle, Phase, Scheduler
from sit_stand_reminder.ui.dashboard import DashboardWindow
from sit_stand_reminder.ui.reminder import ReminderDialog
from sit_stand_reminder.ui.settings import SettingsDialog
from sit_stand_reminder.ui.style import resolve_theme, setup_theme


class App:
    """Main application controller."""

    def __init__(self) -> None:
        self.config = load_config()
        self.scheduler: Scheduler | None = None
        self._reminder_lock = threading.Lock()
        self._reminder_open = False
        self._event_queue: queue.Queue = queue.Queue()
        self._poll_job: str | None = None

        # Hidden root window; all visible UI is Toplevel-based
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Sit-Stand Reminder")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # macOS: intercept application-level Quit so macOS doesn't see a crash
        if platform.system() == "Darwin":
            self.root.createcommand("::tk::mac::Quit", self.quit)

        theme = resolve_theme(self.config.theme)
        self.style = setup_theme(self.root, theme)

        self.dashboard = DashboardWindow(
            self.root,
            self.config,
            on_settings=self.open_settings,
            on_quit=self.quit,
            on_toggle_mute=self._on_mute_toggle,
            on_test_reminder=self._test_reminder,
        )

        cycle = Cycle(self.config.sit_for, self.config.stand_for, self.config.walk_for)
        self.scheduler = Scheduler(
            cycle=cycle,
            event_queue=self._event_queue,
            on_tick=self._on_tick,
        )

        # Show dashboard on startup
        self.dashboard.show()

    def run(self) -> None:
        """Start the scheduler and enter the Tk mainloop."""
        self._start_polling()
        self.scheduler.start()
        self.root.mainloop()
        self.scheduler.stop()
        save_config(self.config)

    def _start_polling(self) -> None:
        """Poll the event queue every 250 ms from the main thread."""
        self._drain_queue()
        self._poll_job = self.root.after(250, self._start_polling)

    def _drain_queue(self) -> None:
        """Process all queued events."""
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                kind = event[0]
                if kind == "tick":
                    _, phase, seconds_left = event
                    self.dashboard.update_state(phase, seconds_left)
                elif kind == "reminder":
                    _, phase = event
                    self._show_reminder(phase)
            except queue.Empty:
                break
            except Exception:
                pass

    def _on_tick(self, phase: Phase, seconds_left: int) -> None:
        """Called every second from the scheduler thread (for diagnostics only)."""
        pass  # Events are pulled via the queue now

    def _on_reminder(self, phase: Phase) -> None:
        """Placeholder for scheduler callback (events go through queue)."""
        pass

    def _show_reminder(self, phase: Phase) -> None:
        with self._reminder_lock:
            if self._reminder_open:
                return
            self._reminder_open = True

        play_audio(PHASE_NAMES[phase], muted=self.config.mute)
        self.dashboard.show()

        dialog = ReminderDialog(
            self.root,
            self.config,
            phase,
            on_done=lambda: self._record_response(phase, "Done"),
            on_skip=lambda: self._record_response(phase, "Skip"),
            on_settings=self.open_settings,
            on_mute_toggle=lambda: save_config(self.config),
        )
        dialog.wait()

        with self._reminder_lock:
            self._reminder_open = False

    def _record_response(self, phase: Phase, response: str) -> None:
        name = PHASE_NAMES[phase]
        if response == "Done":
            self.config.counters[name]["completed"] += 1
        else:
            self.config.counters[name]["ignored"] += 1
        save_config(self.config)
        # Refresh dashboard counters immediately
        if self.dashboard.window.winfo_exists():
            self.dashboard.update_state(phase, 0)

    def _test_reminder(self) -> None:
        """Manually trigger a reminder popup for testing."""
        import random
        phase = random.choice([Phase.SIT, Phase.STAND, Phase.WALK])
        self._show_reminder(phase)

    def open_settings(self) -> None:
        """Open the settings dialog and apply changes on save."""

        def on_save(new_config: AppConfig) -> None:
            self.config = new_config
            save_config(self.config)
            self._restart_scheduler()
            self.dashboard.set_config(self.config)
            # Refresh theme if changed
            theme = resolve_theme(self.config.theme)
            self.style = setup_theme(self.root, theme)

        dialog = SettingsDialog(self.root, self.config, on_save=on_save)
        dialog.wait()

    def _restart_scheduler(self) -> None:
        """Restart the scheduler with the current config cycle."""
        if self.scheduler:
            self.scheduler.stop()
        cycle = Cycle(self.config.sit_for, self.config.stand_for, self.config.walk_for)
        self.scheduler = Scheduler(
            cycle=cycle,
            event_queue=self._event_queue,
            on_tick=self._on_tick,
        )
        self.scheduler.start()

    def _on_mute_toggle(self) -> None:
        save_config(self.config)

    def quit(self) -> None:
        """Gracefully shut down the application."""
        if self._poll_job is not None:
            try:
                self.root.after_cancel(self._poll_job)
            except Exception:
                pass
        if self.scheduler:
            self.scheduler.stop()
        save_config(self.config)
        self.root.destroy()
        # Do NOT call sys.exit(0) here — it causes macOS to report a crash.


def main() -> None:
    app = App()
    app.run()


if __name__ == "__main__":
    main()
