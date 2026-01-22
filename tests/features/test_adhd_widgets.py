#!/usr/bin/env python3
"""Quick test of new ADHD widgets"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.widgets import (
    BreakReminderWidget,
    FocusStreakWidget,
    DistractionBlockerWidget,
    HydrationReminderWidget,
    PomodoroCyclesWidget,
)
from app.state import (
    BreakReminderState,
    FocusStreakState,
    DistractionBlockerState,
    HydrationReminderState,
    PomodoroCyclesState,
    load_state,
    save_state,
    AppState,
)
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from datetime import datetime, timedelta

def test_widgets():
    """Test all new widgets"""
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("ADHD Focus Widgets Test")
    window.setGeometry(100, 100, 800, 900)
    
    # Create container
    container = QWidget()
    layout = QVBoxLayout()
    
    # Add title
    title = QLabel("ADHD Focus Widgets - Quick Test")
    title.setStyleSheet("font-size: 16px; font-weight: bold;")
    layout.addWidget(title)
    
    # Test Break Reminder Widget
    print("✓ Creating BreakReminderWidget...")
    break_widget = BreakReminderWidget()
    layout.addWidget(break_widget)
    
    # Test Focus Streak Widget
    print("✓ Creating FocusStreakWidget...")
    streak_widget = FocusStreakWidget()
    layout.addWidget(streak_widget)
    
    # Test Distraction Blocker Widget
    print("✓ Creating DistractionBlockerWidget...")
    blocker_widget = DistractionBlockerWidget()
    layout.addWidget(blocker_widget)
    
    # Test Hydration Reminder Widget
    print("✓ Creating HydrationReminderWidget...")
    hydration_widget = HydrationReminderWidget()
    layout.addWidget(hydration_widget)
    
    # Test Pomodoro Cycles Widget
    print("✓ Creating PomodoroCyclesWidget...")
    pomodoro_widget = PomodoroCyclesWidget()
    layout.addWidget(pomodoro_widget)
    
    container.setLayout(layout)
    window.setCentralWidget(container)
    window.show()
    
    # Test state persistence
    print("\n" + "="*50)
    print("Testing State Persistence")
    print("="*50)
    
    # Create test state
    test_state = AppState(
        todos=[],
        break_reminder=BreakReminderState(
            last_break_time=datetime.now().isoformat(),
            break_count_today=2
        ),
        focus_streak=FocusStreakState(
            current_streak=5,
            best_streak=10,
            sessions_completed=25
        ),
        distraction_blocker=DistractionBlockerState(
            is_active=False,
        ),
        hydration_reminder=HydrationReminderState(
            last_water_time=datetime.now().isoformat(),
            water_intake_today=3
        ),
        pomodoro_cycles=PomodoroCyclesState(
            cycles_today=4,
            total_focus_time_minutes=100
        )
    )
    
    print("✓ Saving test state...")
    save_state(test_state)
    
    print("✓ Loading state back...")
    loaded = load_state()
    
    print("\nLoaded state:")
    print(f"  - Break reminder: {loaded.break_reminder.break_count_today} breaks today")
    print(f"  - Focus streak: {loaded.focus_streak.current_streak} current, {loaded.focus_streak.best_streak} best")
    print(f"  - DND active: {loaded.distraction_blocker.is_active}")
    print(f"  - Water intake: {loaded.hydration_reminder.water_intake_today} cups")
    print(f"  - Pomodoro cycles: {loaded.pomodoro_cycles.cycles_today} today ({loaded.pomodoro_cycles.total_focus_time_minutes} min)")
    
    print("\n" + "="*50)
    print("✅ All widgets created and state persisted successfully!")
    print("="*50)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_widgets()
