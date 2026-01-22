from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any
from datetime import datetime


STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"


@dataclass
class TodoItem:
    text: str
    done: bool = False


@dataclass
class BreakReminderState:
    last_break_time: str = ""  # ISO format timestamp
    break_count_today: int = 0


@dataclass
class FocusStreakState:
    current_streak: int = 0
    best_streak: int = 0
    last_session_date: str = ""  # ISO format date
    sessions_completed: int = 0


@dataclass
class DistractionBlockerState:
    is_active: bool = False
    blocked_until: str = ""  # ISO format timestamp
    block_reason: str = ""


@dataclass
class HydrationReminderState:
    last_water_time: str = ""  # ISO format timestamp
    water_intake_today: int = 0  # in cups


@dataclass
class PomodoroCyclesState:
    cycles_today: int = 0
    last_cycle_date: str = ""  # ISO format date
    total_focus_time_minutes: int = 0


@dataclass
class AppState:
    todos: list[TodoItem]
    break_reminder: BreakReminderState = None  # type: ignore[assignment]
    focus_streak: FocusStreakState = None  # type: ignore[assignment]
    distraction_blocker: DistractionBlockerState = None  # type: ignore[assignment]
    hydration_reminder: HydrationReminderState = None  # type: ignore[assignment]
    pomodoro_cycles: PomodoroCyclesState = None  # type: ignore[assignment]


def _normalise_state(data: dict[str, Any]) -> AppState:
    raw = data.get("todos", [])
    todos: list[TodoItem] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                text = str(item.get("text", "")).strip()
                if not text:
                    continue
                done = bool(item.get("done", False))
                todos.append(TodoItem(text=text, done=done))
            elif isinstance(item, str):
                t = item.strip()
                if t:
                    todos.append(TodoItem(text=t, done=False))
    
    # Parse break reminder state
    break_data = data.get("break_reminder", {})
    break_reminder = BreakReminderState(
        last_break_time=str(break_data.get("last_break_time", "")),
        break_count_today=int(break_data.get("break_count_today", 0))
    )
    
    # Parse focus streak state
    streak_data = data.get("focus_streak", {})
    focus_streak = FocusStreakState(
        current_streak=int(streak_data.get("current_streak", 0)),
        best_streak=int(streak_data.get("best_streak", 0)),
        last_session_date=str(streak_data.get("last_session_date", "")),
        sessions_completed=int(streak_data.get("sessions_completed", 0))
    )
    
    # Parse distraction blocker state
    blocker_data = data.get("distraction_blocker", {})
    distraction_blocker = DistractionBlockerState(
        is_active=bool(blocker_data.get("is_active", False)),
        blocked_until=str(blocker_data.get("blocked_until", "")),
        block_reason=str(blocker_data.get("block_reason", ""))
    )
    
    # Parse hydration reminder state
    hydration_data = data.get("hydration_reminder", {})
    hydration_reminder = HydrationReminderState(
        last_water_time=str(hydration_data.get("last_water_time", "")),
        water_intake_today=int(hydration_data.get("water_intake_today", 0))
    )
    
    # Parse pomodoro cycles state
    pomodoro_data = data.get("pomodoro_cycles", {})
    pomodoro_cycles = PomodoroCyclesState(
        cycles_today=int(pomodoro_data.get("cycles_today", 0)),
        last_cycle_date=str(pomodoro_data.get("last_cycle_date", "")),
        total_focus_time_minutes=int(pomodoro_data.get("total_focus_time_minutes", 0))
    )
    
    return AppState(
        todos=todos,
        break_reminder=break_reminder,
        focus_streak=focus_streak,
        distraction_blocker=distraction_blocker,
        hydration_reminder=hydration_reminder,
        pomodoro_cycles=pomodoro_cycles
    )


def load_state() -> AppState:
    if not STATE_PATH.exists():
        state = AppState(todos=[])
        save_state(state)
        return state

    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("state.json not a dict")
        return _normalise_state(data)
    except Exception:
        state = AppState(todos=[])
        save_state(state)
        return state


def save_state(state: AppState) -> None:
    payload = {
        "todos": [asdict(t) for t in state.todos],
        "break_reminder": asdict(state.break_reminder) if state.break_reminder else {},
        "focus_streak": asdict(state.focus_streak) if state.focus_streak else {},
        "distraction_blocker": asdict(state.distraction_blocker) if state.distraction_blocker else {},
        "hydration_reminder": asdict(state.hydration_reminder) if state.hydration_reminder else {},
        "pomodoro_cycles": asdict(state.pomodoro_cycles) if state.pomodoro_cycles else {},
    }
    STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

