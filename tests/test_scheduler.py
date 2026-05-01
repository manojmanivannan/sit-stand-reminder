"""Tests for the scheduler module."""

from __future__ import annotations

from datetime import datetime
from queue import Queue
from time import sleep
from unittest.mock import patch

import pytest

from sit_stand_reminder.scheduler import Cycle, Phase, Scheduler


class TestCycle:
    """Tests for the Cycle dataclass."""

    def test_default_total_is_30(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.total == 30
        assert cycle.validate() is None

    def test_invalid_sum(self) -> None:
        cycle = Cycle(10, 10, 15)
        assert cycle.validate() is not None
        assert "35" in cycle.validate()

    def test_invalid_negative(self) -> None:
        cycle = Cycle(-1, 20, 11)
        assert cycle.validate() is not None
        assert "at least 1" in cycle.validate()

    def test_phase_at_minute_sit(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.phase_at_minute(0) == Phase.SIT
        assert cycle.phase_at_minute(10) == Phase.SIT
        assert cycle.phase_at_minute(19) == Phase.SIT

    def test_phase_at_minute_stand(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.phase_at_minute(20) == Phase.STAND
        assert cycle.phase_at_minute(27) == Phase.STAND

    def test_phase_at_minute_walk(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.phase_at_minute(28) == Phase.WALK
        assert cycle.phase_at_minute(29) == Phase.WALK

    def test_phase_at_minute_wraps_every_30(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.phase_at_minute(30) == Phase.SIT
        # 50 % 30 = 20 → boundary, STAND starts at minute 20
        assert cycle.phase_at_minute(50) == Phase.STAND
        assert cycle.phase_at_minute(52) == Phase.STAND
        assert cycle.phase_at_minute(58) == Phase.WALK

    def test_seconds_until_next_sit(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_until_next(0, 0) == 20 * 60
        assert cycle.seconds_until_next(10, 30) == (9 * 60 + 30)

    def test_seconds_until_next_stand(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_until_next(20, 0) == 8 * 60

    def test_seconds_until_next_walk(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_until_next(28, 0) == 2 * 60

    def test_seconds_until_next_boundary(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_until_next(29, 59) == 1

    def test_seconds_into_phase(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_into_phase(10, 30) == 10 * 60 + 30
        assert cycle.seconds_into_phase(22, 15) == 2 * 60 + 15
        assert cycle.seconds_into_phase(28, 0) == 0

    def test_custom_cycle(self) -> None:
        cycle = Cycle(15, 10, 5)
        assert cycle.total == 30
        assert cycle.phase_at_minute(14) == Phase.SIT
        assert cycle.phase_at_minute(15) == Phase.STAND
        assert cycle.phase_at_minute(25) == Phase.WALK

    def test_seconds_until_next_never_negative(self) -> None:
        cycle = Cycle(20, 8, 2)
        assert cycle.seconds_until_next(29, 59) == 1
        assert cycle.seconds_until_next(30, 0) == 20 * 60


class _FakeDatetime:
    """Fake datetime class whose .now() returns from a controlled list."""

    def __init__(self, times: list[datetime]) -> None:
        self._times = times
        self._idx = 0

    def now(self) -> datetime:
        t = self._times[self._idx]
        if self._idx < len(self._times) - 1:
            self._idx += 1
        return t


class TestScheduler:
    """Tests for the Scheduler class."""

    def test_scheduler_pushes_tick_events(self) -> None:
        q = Queue()
        cycle = Cycle(20, 8, 2)
        scheduler = Scheduler(cycle, event_queue=q)
        scheduler.start()
        sleep(2.5)
        scheduler.stop()

        events = []
        while not q.empty():
            events.append(q.get_nowait())

        assert len(events) >= 2
        # Events can be tick or reminder (if first observation happens at second < 3)
        assert all(e[0] in ("tick", "reminder") for e in events)
        tick_events = [e for e in events if e[0] == "tick"]
        assert len(tick_events) >= 2

    def test_scheduler_pushes_reminder_on_phase_change(self) -> None:
        q = Queue()
        cycle = Cycle(20, 8, 2)
        scheduler = Scheduler(cycle, event_queue=q)

        base = datetime(2024, 1, 1, 12, 0, 0)
        fake = _FakeDatetime([
            base,                              # minute 0, second 0  → SIT, reminder
            base.replace(second=1),            # minute 0, second 1  → SIT, no reminder
            base.replace(minute=1, second=0),  # minute 1, second 0  → SIT, no phase change
            base.replace(minute=20, second=0), # minute 20, second 0 → STAND, reminder
            base.replace(minute=20, second=1), # minute 20, second 1 → STAND
            base.replace(minute=20, second=2), # minute 20, second 2 → STAND
            base.replace(minute=20, second=3), # minute 20, second 3 → STAND
        ])

        with patch("sit_stand_reminder.scheduler.sleep", return_value=None):
            with patch("sit_stand_reminder.scheduler.datetime", fake):
                scheduler.start()
                sleep(0.2)
                scheduler.stop()
                if scheduler._thread:
                    scheduler._thread.join(timeout=1)

        events = []
        while not q.empty():
            events.append(q.get_nowait())

        reminder_events = [e for e in events if e[0] == "reminder"]
        tick_events = [e for e in events if e[0] == "tick"]

        assert len(reminder_events) >= 2
        assert len(tick_events) >= 3
        assert reminder_events[0][1] == Phase.SIT
        assert reminder_events[1][1] == Phase.STAND

    def test_scheduler_no_duplicate_start(self) -> None:
        q = Queue()
        cycle = Cycle(20, 8, 2)
        scheduler = Scheduler(cycle, event_queue=q)
        scheduler.start()
        first_thread = scheduler._thread
        scheduler.start()
        assert scheduler._thread is first_thread
        scheduler.stop()

    def test_scheduler_stop_does_not_crash(self) -> None:
        q = Queue()
        cycle = Cycle(20, 8, 2)
        scheduler = Scheduler(cycle, event_queue=q)
        scheduler.start()
        scheduler.stop()
        scheduler.stop()  # Idempotent

    def test_scheduler_first_observation_no_early_reminder(self) -> None:
        """If first observation is at second >= 3, no startup reminder fires."""
        q = Queue()
        cycle = Cycle(20, 8, 2)
        scheduler = Scheduler(cycle, event_queue=q)

        base = datetime(2024, 1, 1, 12, 0, 5)
        fake = _FakeDatetime([
            base,                              # minute 0, second 5  → no reminder
            base.replace(second=6),            # minute 0, second 6  → no reminder
            base.replace(minute=1, second=5), # minute 1, second 5  → still SIT
        ])

        with patch("sit_stand_reminder.scheduler.sleep", return_value=None):
            with patch("sit_stand_reminder.scheduler.datetime", fake):
                scheduler.start()
                sleep(0.2)
                scheduler.stop()
                if scheduler._thread:
                    scheduler._thread.join(timeout=1)

        events = []
        while not q.empty():
            events.append(q.get_nowait())

        reminder_events = [e for e in events if e[0] == "reminder"]
        assert len(reminder_events) == 0
        tick_events = [e for e in events if e[0] == "tick"]
        assert len(tick_events) >= 2
