"""Reminder scheduling logic."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from queue import Queue
from time import sleep
from typing import Callable


class Phase(Enum):
    SIT = auto()
    STAND = auto()
    WALK = auto()


PHASE_NAMES: dict[Phase, str] = {
    Phase.SIT: "SIT DOWN",
    Phase.STAND: "STAND UP",
    Phase.WALK: "WALK",
}


@dataclass
class Cycle:
    """Represents a single 30-minute cycle split into phases."""

    sit: int
    stand: int
    walk: int

    @property
    def total(self) -> int:
        return self.sit + self.stand + self.walk

    def validate(self) -> str | None:
        if self.total != 30:
            return f"Cycle must sum to 30 minutes (got {self.total})."
        if any(v < 1 for v in (self.sit, self.stand, self.walk)):
            return "Each phase must be at least 1 minute."
        return None

    def phase_at_minute(self, minute: int) -> Phase:
        """Return the phase active at a given minute-of-hour (0-59)."""
        m = minute % 30
        if m < self.sit:
            return Phase.SIT
        if m < self.sit + self.stand:
            return Phase.STAND
        return Phase.WALK

    def seconds_into_phase(self, minute: int, second: int) -> int:
        """Return how many seconds into the current phase we are."""
        m = minute % 30
        if m < self.sit:
            start = 0
        elif m < self.sit + self.stand:
            start = self.sit
        else:
            start = self.sit + self.stand
        return (m - start) * 60 + second

    def seconds_until_next(self, minute: int, second: int) -> int:
        """Return seconds remaining until the next phase transition."""
        m = minute % 30
        if m < self.sit:
            boundary = self.sit
        elif m < self.sit + self.stand:
            boundary = self.sit + self.stand
        else:
            boundary = 30
        return max(0, (boundary - m) * 60 - second)


class Scheduler:
    """Runs a background thread that pushes events to a queue."""

    def __init__(
        self,
        cycle: Cycle,
        event_queue: Queue,
        on_tick: Callable[[Phase, int], None] | None = None,
    ):
        self.cycle = cycle
        self.event_queue = event_queue
        self.on_tick = on_tick
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._last_phase: Phase | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _loop(self) -> None:
        last_triggered_minute = -1
        while not self._stop_event.is_set():
            sleep(1)
            try:
                now = datetime.now()
                current_minute = now.minute
                current_second = now.second

                phase = self.cycle.phase_at_minute(current_minute)
                seconds_left = self.cycle.seconds_until_next(current_minute, current_second)

                if self.on_tick:
                    self.on_tick(phase, seconds_left)

                # Push tick event to queue every second
                self.event_queue.put(("tick", phase, seconds_left))

                if current_minute != last_triggered_minute:
                    if self._last_phase is None:
                        if current_second < 3:
                            self.event_queue.put(("reminder", phase))
                    elif phase != self._last_phase:
                        self.event_queue.put(("reminder", phase))
                    self._last_phase = phase
                    last_triggered_minute = current_minute
            except Exception:
                # Prevent thread death on unexpected errors
                pass
