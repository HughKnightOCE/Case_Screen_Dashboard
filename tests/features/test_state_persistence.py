#!/usr/bin/env python3
"""Test ADHD widget state persistence"""

from app.state import load_state, save_state, AppState, BreakReminderState, FocusStreakState, DistractionBlockerState, HydrationReminderState, PomodoroCyclesState
from datetime import datetime, date

# Test creating and saving state with new widgets
print("Testing state persistence...")

state = AppState(
    todos=[],
    break_reminder=BreakReminderState(
        last_break_time=datetime.now().isoformat(),
        break_count_today=3
    ),
    focus_streak=FocusStreakState(
        current_streak=7,
        best_streak=15,
        last_session_date=date.today().isoformat(),
        sessions_completed=42
    ),
    distraction_blocker=DistractionBlockerState(
        is_active=False,
        blocked_until="",
        block_reason=""
    ),
    hydration_reminder=HydrationReminderState(
        last_water_time=datetime.now().isoformat(),
        water_intake_today=4
    ),
    pomodoro_cycles=PomodoroCyclesState(
        cycles_today=6,
        last_cycle_date=date.today().isoformat(),
        total_focus_time_minutes=150
    )
)

print("✓ Creating test state...")
save_state(state)
print("✓ State saved to state.json")

loaded = load_state()
print("\n✓ State loaded back:")
print(f"  Todos: {len(loaded.todos)}")
print(f"  Break reminders: {loaded.break_reminder.break_count_today} breaks")
print(f"  Focus streak: {loaded.focus_streak.current_streak} current (best: {loaded.focus_streak.best_streak})")
print(f"  Sessions completed: {loaded.focus_streak.sessions_completed}")
print(f"  DND active: {loaded.distraction_blocker.is_active}")
print(f"  Water intake: {loaded.hydration_reminder.water_intake_today} cups")
print(f"  Pomodoro cycles: {loaded.pomodoro_cycles.cycles_today} (total {loaded.pomodoro_cycles.total_focus_time_minutes} min)")
