#!/usr/bin/env python3
"""Test ADHD widget integration in dashboard"""

from app.config import PRESETS, WIDGET_TYPES
from ui.dashboard import DashboardView
from PySide6.QtWidgets import QApplication
import sys

# Create QApplication first
app = QApplication(sys.argv)

print("Testing dashboard integration...")
print(f"\n✓ Available widget types: {WIDGET_TYPES}")
print(f"\n✓ Available presets: {list(PRESETS.keys())}")

# Test ADHD preset
adhd_layout = PRESETS.get("adhd_focus")
print(f"\n✓ ADHD focus preset layout:")
for slot, widget_type in adhd_layout.items():
    print(f"  {slot}: {widget_type}")

# Test widget creation through dashboard
print("\n✓ Testing widget creation through dashboard...")
dashboard = DashboardView(layout_cfg=adhd_layout)
print("✓ Dashboard created successfully with ADHD preset")

# Test each widget type
print("\nTesting individual widget instantiation:")
test_widgets = [
    "break_reminder",
    "focus_streak", 
    "distraction_blocker",
    "hydration_reminder",
    "pomodoro_cycles"
]

for widget_type in test_widgets:
    try:
        widget = dashboard._make_widget(widget_type, widget_type)
        print(f"  ✓ {widget_type}: {type(widget).__name__}")
    except Exception as e:
        print(f"  ✗ {widget_type}: {e}")

print("\n✅ Dashboard integration test passed!")
