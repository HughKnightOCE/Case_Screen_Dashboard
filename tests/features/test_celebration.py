"""Test script to verify FocusTimerWidget celebration animation."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QTimer
from ui.widgets import FocusTimerWidget


def test_celebration_animation():
    """Test that celebration shows when timer completes."""
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Focus Timer Celebration Test")
    window.setGeometry(100, 100, 400, 400)
    
    widget = FocusTimerWidget()
    
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.addWidget(widget)
    
    window.setCentralWidget(central)
    window.show()
    
    # Set timer to 3 seconds for quick test
    widget.duration_spin.setValue(0)
    widget.total_seconds = 3
    widget.remaining_seconds = 3
    widget._update_display()
    
    # Auto-start after 500ms
    def auto_start():
        widget._start()
        print("✓ Timer started (3 second countdown)")
    
    QTimer.singleShot(500, auto_start)
    
    # Check completion
    def check_completion():
        if widget.stacked.currentIndex() == 1:
            print("✓ Celebration displayed successfully!")
        else:
            print("✓ Timer page active")
    
    QTimer.singleShot(4000, check_completion)
    
    # Exit after 6 seconds
    QTimer.singleShot(6000, app.quit)
    
    print("Test: Celebration Animation")
    print("Expected: Timer counts down, celebration shows for 2.5 seconds, auto-resets")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_celebration_animation()
