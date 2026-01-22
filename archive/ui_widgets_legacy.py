from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import Qt, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFrame,
    QMessageBox,
    QDialog,
    QSpinBox,
    QProgressBar,
    QStackedWidget,
)

from app.state import (
    TodoItem,
    save_state,
    AppState,
    BreakReminderState,
    FocusStreakState,
    DistractionBlockerState,
    HydrationReminderState,
    PomodoroCyclesState,
)


# =========================
# Base Panel (FIX)
# =========================

class Panel(QFrame):
    """
    Base container used by ui.panels.*
    Provides a title header and a body_layout for child widgets.
    """

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("panel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title.lower())
        self.title_label.setObjectName("panelTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addWidget(self.title_label)
        root.addLayout(header_layout)

        # Body
        body = QWidget(self)
        body.setObjectName("panelBody")

        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(4, 4, 4, 4)
        self.body_layout.setSpacing(12)

        root.addWidget(body, 1)


# =========================
# Widgets
# =========================

class MetricTile(QWidget):
    """Displays a metric label with value and unit."""
    
    def __init__(self, label: str, value: str = "--", unit: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("metricTile")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        self.label = QLabel(label.lower())
        self.label.setObjectName("metricLabel")

        self.value = QLabel(value)
        self.value.setObjectName("metricValue")
        self.value.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.unit = QLabel(unit)
        self.unit.setObjectName("metricUnit")
        self.unit.setStyleSheet("font-size: 12px; color: #8aa0b5;")

        layout.addWidget(self.label)
        layout.addWidget(self.value)
        layout.addWidget(self.unit)

    def set_value(self, value: Any) -> None:
        """Update the metric value with proper formatting."""
        if isinstance(value, (int, float)):
            # Format numeric values with 1 decimal place
            formatted = f"{float(value):.1f}"
        else:
            formatted = str(value)
        self.value.setText(formatted)


class ClockWidget(QLabel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("clock")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

    def update_time(self) -> None:
        from datetime import datetime
        self.setText(datetime.now().strftime("%H:%M:%S"))


class StatusList(QListWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("statusList")

    def add_status(self, text: str) -> None:
        item = QListWidgetItem(text)
        self.addItem(item)
        self.scrollToBottom()


@dataclass
class ToggleOption:
    label: str
    checked: bool = False


class ToggleList(QWidget):
    def __init__(self, options: list[ToggleOption], parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.checkboxes: list[QCheckBox] = []

        for opt in options:
            cb = QCheckBox(opt.label)
            cb.setChecked(opt.checked)
            layout.addWidget(cb)
            self.checkboxes.append(cb)

    def values(self) -> list[bool]:
        return [cb.isChecked() for cb in self.checkboxes]


class TodoTable(QWidget):
    """
    Table for displaying and editing todo items inline.
    Supports editing task details and marking items as done.
    """
    
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["unit", "task", "due", "done"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Make the table readable by forcing reasonable font sizes and stretching columns
        self.table.setStyleSheet(
            "QTableWidget { font-size: 14px; } QTableWidget::item { padding: 6px; } QHeaderView::section { font-size: 13px; }"
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Enable editing for all cells except the done column
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked | 
            QTableWidget.EditTrigger.EditKeyPressed
        )
        # Connect item changed signal for potential auto-save
        self.table.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self.table)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Called when an item is edited."""
        # Could emit a signal here for parent to save state
        pass

    def load(self, items: list[dict[str, Any]]) -> None:
        """Load items into the table from a list of dictionaries."""
        self.table.setRowCount(0)

        for it in items:
            unit = str(it.get("unit", "")).strip()
            task = str(it.get("task", "")).strip()
            due = str(it.get("due", "")).strip()
            done = bool(it.get("done", False))

            r = self.table.rowCount()
            self.table.insertRow(r)
            
            # Unit column (editable)
            unit_item = QTableWidgetItem(unit)
            self.table.setItem(r, 0, unit_item)
            
            # Task column (editable)
            task_item = QTableWidgetItem(task)
            self.table.setItem(r, 1, task_item)
            
            # Due column (editable)
            due_item = QTableWidgetItem(due)
            self.table.setItem(r, 2, due_item)

            # Done column (checkbox)
            done_item = QTableWidgetItem("")
            done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            done_item.setCheckState(
                Qt.CheckState.Checked if done else Qt.CheckState.Unchecked
            )
            self.table.setItem(r, 3, done_item)
            
            # Visual feedback for completed items
            if done:
                for col in range(4):
                    cell = self.table.item(r, col)
                    cell.setForeground(QColor("#888888"))

    def get_items(self) -> list[dict[str, Any]]:
        """Extract current items from table."""
        items = []
        for r in range(self.table.rowCount()):
            unit = str(self.table.item(r, 0).text() or "").strip()
            task = str(self.table.item(r, 1).text() or "").strip()
            due = str(self.table.item(r, 2).text() or "").strip()
            done = self.table.item(r, 3).checkState() == Qt.CheckState.Checked
            
            if task:  # Only include if task is not empty
                items.append({
                    "unit": unit,
                    "task": task,
                    "due": due,
                    "done": done
                })
        return items


class TodoListWidget(QWidget):
    """
    Displays a list of todo items with inline editing and add/delete buttons.
    Supports checkbox toggling and automatic state persistence.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Input area for new tasks
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)
        
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Add a new task...")
        self.input.returnPressed.connect(self._add_item_from_input)
        self.input.setStyleSheet("font-size: 16px; padding: 6px;")
        input_layout.addWidget(self.input)
        
        self.add_btn = QPushButton("Add")
        self.add_btn.setFixedWidth(60)
        self.add_btn.setStyleSheet("font-size: 14px;")
        self.add_btn.clicked.connect(self._add_item_from_input)
        input_layout.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedWidth(60)
        self.delete_btn.setStyleSheet("font-size: 14px;")
        self.delete_btn.clicked.connect(self._delete_selected)
        input_layout.addWidget(self.delete_btn)
        
        layout.addLayout(input_layout)

        # List of items
        self.list = QListWidget(self)
        self.list.setStyleSheet("font-size: 16px;")
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list)

    def set_items(self, items: list[TodoItem]) -> None:
        """Load items into the list."""
        self.list.blockSignals(True)  # Prevent item changed signals during load
        self.list.clear()
        for t in items:
            it = QListWidgetItem(self.list)
            it.setData(Qt.ItemDataRole.UserRole, t.text)
            it.setText(t.text)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            it.setCheckState(Qt.CheckState.Checked if t.done else Qt.CheckState.Unchecked)
            
            # Visual feedback for completed items
            if t.done:
                it.setForeground(QColor("#888888"))
        self.list.blockSignals(False)

    def get_items(self) -> list[TodoItem]:
        """Extract current items from the list."""
        items: list[TodoItem] = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            text = str(it.text() or "").strip()
            done = bool(it.checkState() == Qt.CheckState.Checked)
            if text:
                items.append(TodoItem(text=text, done=done))
        return items

    def _add_item_from_input(self) -> None:
        """Add a new item from the input field."""
        text = self.input.text().strip()
        if not text:
            return
        
        it = QListWidgetItem(self.list)
        it.setData(Qt.ItemDataRole.UserRole, text)
        it.setText(text)
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
        it.setCheckState(Qt.CheckState.Unchecked)
        self.list.addItem(it)
        
        self.input.clear()
        self._persist_state()

    def _delete_selected(self) -> None:
        """Delete the currently selected item."""
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)
            self._persist_state()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Toggle done state on double-click."""
        new_state = (
            Qt.CheckState.Unchecked 
            if item.checkState() == Qt.CheckState.Checked 
            else Qt.CheckState.Checked
        )
        item.setCheckState(new_state)
        
        # Update visual feedback
        if new_state == Qt.CheckState.Checked:
            item.setForeground(QColor("#888888"))
        else:
            item.setForeground(QColor("#000000"))

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        """Called when item text or state changes."""
        self._persist_state()

    def _persist_state(self) -> None:
        """Save current state to state.json."""
        try:
            todos = self.get_items()
            state = AppState(todos=todos)
            save_state(state)
        except Exception as e:
            print(f"Error persisting todo state: {e}")


class UniTasksWidget(TodoTable):
    """
    Displays university tasks loaded from uni_tasks.json.
    Supports inline editing and persistence to the file.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._load_tasks()
        
        # Add button to add new task
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(8)
        
        self.add_btn = QPushButton("Add Task")
        self.add_btn.clicked.connect(self._add_new_row)
        button_layout.addWidget(self.add_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_tasks)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        # Insert button layout into main layout
        self.layout().insertLayout(0, button_layout)

    def _load_tasks(self) -> None:
        """Load university tasks from uni_tasks.json."""
        try:
            tasks_file = Path(__file__).resolve().parents[2] / "uni_tasks.json"
            if tasks_file.exists():
                data = json.loads(tasks_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.load(data)
                else:
                    self._use_fallback_data()
            else:
                self._use_fallback_data()
        except Exception as e:
            print(f"Error loading uni_tasks.json: {e}")
            self._use_fallback_data()

    def _use_fallback_data(self) -> None:
        """Use fallback data if file doesn't exist."""
        self.load([
            {"unit": "CS101", "task": "Assignment 1", "due": "2026-01-30", "done": False},
            {"unit": "MATH200", "task": "Problem Set 3", "due": "2026-02-05", "done": True},
        ])

    def _add_new_row(self) -> None:
        """Add a new empty row to the table."""
        r = self.table.rowCount()
        self.table.insertRow(r)
        
        # Create editable items
        unit_item = QTableWidgetItem("")
        self.table.setItem(r, 0, unit_item)
        
        task_item = QTableWidgetItem("")
        self.table.setItem(r, 1, task_item)
        
        due_item = QTableWidgetItem("")
        self.table.setItem(r, 2, due_item)
        
        # Done checkbox
        done_item = QTableWidgetItem("")
        done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        done_item.setCheckState(Qt.CheckState.Unchecked)
        self.table.setItem(r, 3, done_item)
        
        # Focus on the new task field
        self.table.setCurrentCell(r, 1)
        self.table.editItem(self.table.item(r, 1))

    def _save_tasks(self) -> None:
        """Save tasks to uni_tasks.json."""
        try:
            tasks_file = Path(__file__).resolve().parents[2] / "uni_tasks.json"
            items = self.get_items()
            tasks_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
            print(f"Saved {len(items)} tasks to uni_tasks.json")
        except Exception as e:
            print(f"Error saving uni_tasks.json: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save tasks: {e}")


class FocusTimerWidget(QWidget):
    """
    A pomodoro/focus timer widget with start/pause/reset controls.
    Timer counts down from 25 minutes and provides visual feedback.
    Features celebratory animation when timer completes.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Stacked widget to overlay celebration on timer
        self.stacked = QStackedWidget(self)
        
        # Timer page (normal view)
        timer_widget = QWidget()
        timer_layout = QVBoxLayout(timer_widget)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(0)
        
        # Timer display
        self.label = QLabel("25:00", self)
        self.label.setObjectName("timerLabel")
        self.label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.label)
        
        self.stacked.addWidget(timer_widget)
        
        # Celebration page
        celebration_widget = QWidget()
        celebration_layout = QVBoxLayout(celebration_widget)
        celebration_layout.setContentsMargins(0, 0, 0, 0)
        celebration_layout.setSpacing(8)
        
        # Celebrate message
        self.celebration_label = QLabel("🎉 WELL DONE! 🎉", self)
        self.celebration_label.setObjectName("celebrationLabel")
        self.celebration_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #FFD700; "
            "background-color: rgba(255, 215, 0, 20); border-radius: 8px; padding: 12px;"
        )
        self.celebration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        celebration_layout.addWidget(self.celebration_label)
        
        # Fireworks animation label
        self.fireworks_label = QLabel("✨ ✨ ✨", self)
        self.fireworks_label.setStyleSheet("font-size: 20px; color: #FFD700;")
        self.fireworks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        celebration_layout.addWidget(self.fireworks_label)
        
        # Keep dimmed timer visible underneath
        self.dimmed_timer_label = QLabel("25:00", self)
        self.dimmed_timer_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: rgba(51, 51, 51, 0.3);"
        )
        self.dimmed_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        celebration_layout.addWidget(self.dimmed_timer_label)
        
        celebration_layout.addStretch()
        self.stacked.addWidget(celebration_widget)
        
        layout.addWidget(self.stacked)

        # Duration selector (allow user to change timer length)
        duration_layout = QHBoxLayout()
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(8)
        
        duration_label = QLabel("Minutes:")
        duration_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.duration_spin = QSpinBox(self)
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(60)
        self.duration_spin.setValue(25)
        self.duration_spin.setFixedWidth(60)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spin)
        duration_layout.addStretch()
        layout.addLayout(duration_layout)

        # Timer logic
        self.total_seconds = 25 * 60  # 25 minutes
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        
        # Celebration timer and animation
        self.celebration_timer = QTimer(self)
        self.celebration_timer.timeout.connect(self._animate_celebration)
        self.celebration_frame = 0

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.start_btn = QPushButton("Start", self)
        self.start_btn.clicked.connect(self._start)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px; font-size: 18px; }")
        btn_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause", self)
        self.pause_btn.clicked.connect(self._pause)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px; border-radius: 4px; font-size: 18px; } QPushButton:disabled { background-color: #ccc; }")
        btn_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.clicked.connect(self._reset)
        self.reset_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; border-radius: 4px; font-size: 18px; }")
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        self._update_display()

    def _on_duration_changed(self, minutes: int) -> None:
        """Called when duration spinbox changes."""
        if not self.is_running:
            self.total_seconds = minutes * 60
            self.remaining_seconds = self.total_seconds
            self._update_display()

    def _update_display(self) -> None:
        """Update the timer display label."""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.label.setText(time_str)
        self.dimmed_timer_label.setText(time_str)
        
        # Change color based on time remaining (visual feedback)
        if self.remaining_seconds <= 0:
            self.label.setStyleSheet("font-size: 28px; font-weight: bold; color: #f44336;")  # Red
        elif self.remaining_seconds <= 5 * 60:  # Last 5 minutes
            self.label.setStyleSheet("font-size: 28px; font-weight: bold; color: #FF9800;")  # Orange
        else:
            self.label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50;")  # Green

    def _update_timer(self) -> None:
        """Called every second while timer is running."""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
        else:
            self.timer.stop()
            self.is_running = False
            self._show_celebration()

    def _show_celebration(self) -> None:
        """Show celebratory animation when timer completes."""
        self.stacked.setCurrentIndex(1)  # Show celebration page
        self.celebration_frame = 0
        self.celebration_timer.start(200)  # Update every 200ms for animation
        
        # Auto-dismiss after 2.5 seconds
        QTimer.singleShot(2500, self._hide_celebration)

    def _animate_celebration(self) -> None:
        """Animate the celebration with bouncing fireworks."""
        frames = [
            "✨ ✨ ✨",
            "✨   ✨   ✨",
            "✨ ✨ ✨",
            "  ✨   ✨  ",
        ]
        self.celebration_frame = (self.celebration_frame + 1) % len(frames)
        self.fireworks_label.setText(frames[self.celebration_frame])

    def _hide_celebration(self) -> None:
        """Hide celebration and reset timer."""
        self.celebration_timer.stop()
        self.stacked.setCurrentIndex(0)  # Show timer page
        self._reset()

    def _start(self) -> None:
        """Start the timer."""
        if not self.timer.isActive() and self.remaining_seconds > 0:
            self.timer.start(1000)
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.duration_spin.setEnabled(False)

    def _pause(self) -> None:
        """Pause the timer."""
        self.timer.stop()
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.duration_spin.setEnabled(True)

    def _reset(self) -> None:
        """Reset the timer."""
        self.timer.stop()
        self.celebration_timer.stop()
        self.is_running = False
        self.remaining_seconds = self.total_seconds
        self._update_display()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.duration_spin.setEnabled(True)
        self.stacked.setCurrentIndex(0)  # Ensure timer page is visible

# =========================
# ADHD/Focus Widgets
# =========================

class BreakReminderWidget(QWidget):
    """
    Shows elapsed time since last break and suggests taking one every 30 minutes.
    ADHD-friendly: bright colors, clear status, motivational messages.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Status indicator
        self.status_label = QLabel("break status")
        self.status_label.setObjectName("breakStatus")
        self.status_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Time display
        self.time_label = QLabel("0 min")
        self.time_label.setObjectName("breakTime")
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)

        # Motivation message
        self.message_label = QLabel("You're doing great! Take a break soon 🌟")
        self.message_label.setObjectName("breakMessage")
        self.message_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        # Button
        self.break_btn = QPushButton("Take a Break ☕")
        self.break_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 18px; }")
        self.break_btn.clicked.connect(self._take_break)
        layout.addWidget(self.break_btn)

        # Timer for updating display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_display)
        self.timer.start(60000)  # Update every minute

        self._state = BreakReminderState()
        self._load_state()
        self._update_display()

    def _load_state(self) -> None:
        """Load break reminder state from state.json."""
        try:
            from app.state import load_state
            state = load_state()
            if state.break_reminder:
                self._state = state.break_reminder
        except Exception:
            pass

    def _update_display(self) -> None:
        """Update the display based on elapsed time."""
        from datetime import datetime, timedelta
        
        if not self._state.last_break_time:
            self.time_label.setText("0 min")
            self.status_label.setText("no break yet")
            self.status_label.setStyleSheet("font-size: 12px; color: #FF5722; font-weight: bold;")
            return
            
        try:
            last_break = datetime.fromisoformat(self._state.last_break_time)
            elapsed = datetime.now() - last_break
            minutes = int(elapsed.total_seconds() / 60)
            
            self.time_label.setText(f"{minutes} min")
            
            if minutes < 30:
                self.status_label.setText(f"last break: {minutes} min ago")
                self.status_label.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold;")
                self.time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
                self.message_label.setText("You're in the zone! Keep going 🚀")
            else:
                self.status_label.setText("break recommended!")
                self.status_label.setStyleSheet("font-size: 12px; color: #FF5722; font-weight: bold;")
                self.time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF5722;")
                self.message_label.setText("Time for a break! Rest your eyes and mind 👁️")
        except Exception:
            pass

    def _take_break(self) -> None:
        """Record a break and save state."""
        from datetime import datetime
        self._state.last_break_time = datetime.now().isoformat()
        self._state.break_count_today += 1
        self._save_state()
        self._update_display()

    def _save_state(self) -> None:
        """Save state to state.json."""
        try:
            from app.state import load_state
            state = load_state()
            state.break_reminder = self._state
            save_state(state)
        except Exception as e:
            print(f"Error saving break reminder state: {e}")

    def get_state(self) -> BreakReminderState:
        """Get current state."""
        return self._state

    def set_state(self, state: BreakReminderState) -> None:
        """Set state from external source."""
        self._state = state
        self._update_display()


class FocusStreakWidget(QWidget):
    """
    Tracks consecutive focus sessions completed.
    Shows current streak, celebrates milestones (5, 10, 25, 50 sessions).
    ADHD-friendly: visual progress, celebration messages.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Streak display
        self.streak_label = QLabel("streak")
        self.streak_label.setObjectName("streakLabel")
        self.streak_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(self.streak_label)

        # Big number
        self.streak_number = QLabel("0")
        self.streak_number.setObjectName("streakNumber")
        self.streak_number.setStyleSheet("font-size: 32px; font-weight: bold; color: #FF6F00;")
        self.streak_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.streak_number)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("streakProgress")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #FF6F00;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #FF6F00;
            }
        """)
        self.progress_bar.setMaximum(50)
        layout.addWidget(self.progress_bar)

        # Milestone message
        self.milestone_label = QLabel("")
        self.milestone_label.setObjectName("milestoneLabelStreak")
        self.milestone_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic; font-weight: bold;")
        self.milestone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.milestone_label)

        # Add session button
        self.add_btn = QPushButton("✓ Session Complete")
        self.add_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 18px; }")
        self.add_btn.clicked.connect(self._add_session)
        layout.addWidget(self.add_btn)

        self._state = FocusStreakState()
        self._load_state()
        self._update_display()

    def _load_state(self) -> None:
        """Load focus streak state from state.json."""
        try:
            from app.state import load_state
            state = load_state()
            if state.focus_streak:
                self._state = state.focus_streak
        except Exception:
            pass

    def _update_display(self) -> None:
        """Update the display based on streak."""
        self.streak_number.setText(str(self._state.current_streak))
        
        # Update progress bar
        progress = min(self._state.current_streak, 50)
        self.progress_bar.setValue(progress)
        
        # Check for milestones
        milestone_msg = ""
        if self._state.current_streak == 5:
            milestone_msg = "🎉 5 Sessions! Great work!"
        elif self._state.current_streak == 10:
            milestone_msg = "🌟 10 Sessions! You're unstoppable!"
        elif self._state.current_streak == 25:
            milestone_msg = "🏆 25 Sessions! Focus champion!"
        elif self._state.current_streak == 50:
            milestone_msg = "👑 50 Sessions! Legendary!"
        
        if milestone_msg:
            self.milestone_label.setText(milestone_msg)
            self.streak_number.setStyleSheet("font-size: 36px; font-weight: bold; color: #FFD700;")
        else:
            self.streak_label.setText(f"current streak: {self._state.current_streak} sessions")
            self.streak_number.setStyleSheet("font-size: 32px; font-weight: bold; color: #FF6F00;")

    def _add_session(self) -> None:
        """Add a completed session."""
        from datetime import date
        today = date.today().isoformat()
        
        if self._state.last_session_date != today:
            self._state.current_streak = 1
            self._state.last_session_date = today
        else:
            self._state.current_streak += 1
        
        self._state.sessions_completed += 1
        if self._state.current_streak > self._state.best_streak:
            self._state.best_streak = self._state.current_streak
        
        self._save_state()
        self._update_display()

    def _save_state(self) -> None:
        """Save state to state.json."""
        try:
            from app.state import load_state
            state = load_state()
            state.focus_streak = self._state
            save_state(state)
        except Exception as e:
            print(f"Error saving focus streak state: {e}")

    def get_state(self) -> FocusStreakState:
        """Get current state."""
        return self._state

    def set_state(self, state: FocusStreakState) -> None:
        """Set state from external source."""
        self._state = state
        self._update_display()


class DistractionBlockerWidget(QWidget):
    """
    Shows distraction categories and allows "Do Not Disturb" mode.
    Quick toggle buttons for different block durations (15, 30, 60 min).
    ADHD-friendly: visual on/off indicator.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Status indicator
        self.status_label = QLabel("dnd mode")
        self.status_label.setObjectName("dndStatus")
        self.status_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Timer display
        self.timer_label = QLabel("OFF")
        self.timer_label.setObjectName("dndTimer")
        self.timer_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)

        # Quick toggle buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(6)

        for minutes, label in [(15, "15m"), (30, "30m"), (60, "1h")]:
            btn = QPushButton(label)
            btn.setFixedWidth(50)
            btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 6px; border-radius: 3px; }")
            btn.clicked.connect(lambda checked, m=minutes: self._activate_dnd(m))
            buttons_layout.addWidget(btn)

        # Turn off button
        off_btn = QPushButton("Off")
        off_btn.setFixedWidth(50)
        off_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 6px; border-radius: 3px; }")
        off_btn.clicked.connect(self._deactivate_dnd)
        buttons_layout.addWidget(off_btn)

        layout.addLayout(buttons_layout)

        # Category list (informational)
        categories_label = QLabel("blocked categories: social, notifications, games")
        categories_label.setObjectName("blockedCategories")
        categories_label.setStyleSheet("font-size: 10px; color: #999; font-style: italic;")
        categories_label.setWordWrap(True)
        layout.addWidget(categories_label)

        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.start(1000)

        self._state = DistractionBlockerState()
        self._load_state()
        self._update_display()

    def _load_state(self) -> None:
        """Load distraction blocker state from state.json."""
        try:
            from app.state import load_state
            state = load_state()
            if state.distraction_blocker:
                self._state = state.distraction_blocker
        except Exception:
            pass

    def _activate_dnd(self, minutes: int) -> None:
        """Activate Do Not Disturb mode for specified minutes."""
        from datetime import datetime, timedelta
        blocked_until = datetime.now() + timedelta(minutes=minutes)
        self._state.is_active = True
        self._state.blocked_until = blocked_until.isoformat()
        self._state.block_reason = f"User-initiated block ({minutes} min)"
        self._save_state()
        self._update_display()

    def _deactivate_dnd(self) -> None:
        """Turn off Do Not Disturb mode."""
        self._state.is_active = False
        self._state.blocked_until = ""
        self._save_state()
        self._update_display()

    def _update_timer(self) -> None:
        """Update the timer display."""
        from datetime import datetime
        
        if not self._state.is_active:
            self.timer_label.setText("OFF")
            self.timer_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50;")
            self.status_label.setText("dnd mode: off")
            return
        
        try:
            blocked_until = datetime.fromisoformat(self._state.blocked_until)
            now = datetime.now()
            
            if now >= blocked_until:
                self._deactivate_dnd()
                return
            
            remaining = blocked_until - now
            minutes = int(remaining.total_seconds() / 60)
            seconds = int(remaining.total_seconds() % 60)
            
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            self.timer_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #FF5722;")
            self.status_label.setText(f"dnd mode: on ({self._state.block_reason})")
        except Exception:
            pass

    def _update_display(self) -> None:
        """Update the display."""
        self._update_timer()

    def _save_state(self) -> None:
        """Save state to state.json."""
        try:
            from app.state import load_state
            state = load_state()
            state.distraction_blocker = self._state
            save_state(state)
        except Exception as e:
            print(f"Error saving distraction blocker state: {e}")

    def get_state(self) -> DistractionBlockerState:
        """Get current state."""
        return self._state

    def set_state(self, state: DistractionBlockerState) -> None:
        """Set state from external source."""
        self._state = state
        self._update_display()


class HydrationReminderWidget(QWidget):
    """
    Reminds to drink water every 30 minutes.
    Tracks daily water intake with visual progress.
    ADHD-friendly: clear reminders, motivational feedback.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Status label
        self.status_label = QLabel("hydration")
        self.status_label.setObjectName("hydrationStatus")
        self.status_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Water count display
        self.water_count_label = QLabel("0 cups")
        self.water_count_label.setObjectName("waterCount")
        self.water_count_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        self.water_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.water_count_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("hydrationProgress")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.progress_bar.setMaximum(8)
        layout.addWidget(self.progress_bar)

        # Motivation message
        self.message_label = QLabel("💧 Drink water to stay focused!")
        self.message_label.setObjectName("hydrationMessage")
        self.message_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        # Log water button
        self.water_btn = QPushButton("💧 I drank water")
        self.water_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 16px; }")
        self.water_btn.clicked.connect(self._log_water)
        layout.addWidget(self.water_btn)

        # Update timer (30 minute interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_reminder)
        self.timer.start(30000)  # Every 30 seconds for demo, use 1800000 for production

        self._state = HydrationReminderState()
        self._load_state()
        self._update_display()

    def _load_state(self) -> None:
        """Load hydration reminder state from state.json."""
        try:
            from app.state import load_state
            state = load_state()
            if state.hydration_reminder:
                self._state = state.hydration_reminder
        except Exception:
            pass

    def _check_reminder(self) -> None:
        """Check if it's time to remind about water."""
        from datetime import datetime, timedelta
        
        if not self._state.last_water_time:
            self.status_label.setText("time to drink water! 💧")
            self.status_label.setStyleSheet("font-size: 12px; color: #FF5722; font-weight: bold;")
            return
        
        try:
            last_water = datetime.fromisoformat(self._state.last_water_time)
            elapsed = datetime.now() - last_water
            
            if elapsed > timedelta(minutes=30):
                self.status_label.setText("time to drink water! 💧")
                self.status_label.setStyleSheet("font-size: 12px; color: #FF5722; font-weight: bold;")
            else:
                self.status_label.setText("hydration on track ✓")
                self.status_label.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold;")
        except Exception:
            pass

    def _log_water(self) -> None:
        """Log water intake."""
        from datetime import datetime, date
        
        today = date.today().isoformat()
        # Reset count if new day
        if not self._state.last_water_time.startswith(today):
            self._state.water_intake_today = 0
        
        self._state.last_water_time = datetime.now().isoformat()
        self._state.water_intake_today += 1
        
        self._save_state()
        self._update_display()
        self._check_reminder()

    def _update_display(self) -> None:
        """Update the display."""
        self.water_count_label.setText(f"{self._state.water_intake_today} cups")
        self.progress_bar.setValue(self._state.water_intake_today)
        
        if self._state.water_intake_today >= 8:
            self.message_label.setText("🌟 Great! You've met your daily goal!")
        elif self._state.water_intake_today >= 5:
            self.message_label.setText("👍 Nice work! Keep it up!")
        else:
            self.message_label.setText("💧 Drink more water to stay focused!")
        
        self._check_reminder()

    def _save_state(self) -> None:
        """Save state to state.json."""
        try:
            from app.state import load_state
            state = load_state()
            state.hydration_reminder = self._state
            save_state(state)
        except Exception as e:
            print(f"Error saving hydration reminder state: {e}")

    def get_state(self) -> HydrationReminderState:
        """Get current state."""
        return self._state

    def set_state(self, state: HydrationReminderState) -> None:
        """Set state from external source."""
        self._state = state
        self._update_display()


class PomodoroCyclesWidget(QWidget):
    """
    Tracks completed pomodoro cycles (distinct from the focus timer).
    Shows cycles completed today, estimated time focused.
    ADHD-friendly: clear statistics, encouraging messages.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title
        self.title_label = QLabel("pomodoro cycles")
        self.title_label.setObjectName("pomodoroTitle")
        self.title_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Cycles display
        cycles_layout = QHBoxLayout()
        cycles_layout.setContentsMargins(0, 0, 0, 0)
        cycles_layout.setSpacing(16)

        # Today's cycles
        today_inner = QVBoxLayout()
        today_label = QLabel("today")
        today_label.setStyleSheet("font-size: 11px; color: #999;")
        self.today_cycles = QLabel("0")
        self.today_cycles.setStyleSheet("font-size: 28px; font-weight: bold; color: #FF6F00;")
        self.today_cycles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        today_inner.addWidget(today_label)
        today_inner.addWidget(self.today_cycles)
        cycles_layout.addLayout(today_inner)

        # Estimated focus time
        time_inner = QVBoxLayout()
        time_label = QLabel("focus time")
        time_label.setStyleSheet("font-size: 11px; color: #999;")
        self.focus_time = QLabel("0h 0m")
        self.focus_time.setStyleSheet("font-size: 28px; font-weight: bold; color: #2196F3;")
        self.focus_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_inner.addWidget(time_label)
        time_inner.addWidget(self.focus_time)
        cycles_layout.addLayout(time_inner)

        layout.addLayout(cycles_layout)

        # Recommendation
        self.recommendation_label = QLabel("")
        self.recommendation_label.setObjectName("pomodoroRecommendation")
        self.recommendation_label.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        self.recommendation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.recommendation_label)

        # Log cycle button
        self.log_btn = QPushButton("✓ Complete Cycle")
        self.log_btn.setStyleSheet("QPushButton { background-color: #FF6F00; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 16px; }")
        self.log_btn.clicked.connect(self._log_cycle)
        layout.addWidget(self.log_btn)

        self._state = PomodoroCyclesState()
        self._load_state()
        self._update_display()

    def _load_state(self) -> None:
        """Load pomodoro cycles state from state.json."""
        try:
            from app.state import load_state
            state = load_state()
            if state.pomodoro_cycles:
                self._state = state.pomodoro_cycles
        except Exception:
            pass

    def _log_cycle(self) -> None:
        """Log a completed pomodoro cycle (25 minutes by default)."""
        from datetime import date
        
        today = date.today().isoformat()
        if self._state.last_cycle_date != today:
            self._state.cycles_today = 1
            self._state.last_cycle_date = today
            self._state.total_focus_time_minutes = 25
        else:
            self._state.cycles_today += 1
            self._state.total_focus_time_minutes += 25
        
        self._save_state()
        self._update_display()

    def _update_display(self) -> None:
        """Update the display."""
        self.today_cycles.setText(str(self._state.cycles_today))
        
        hours = self._state.total_focus_time_minutes // 60
        minutes = self._state.total_focus_time_minutes % 60
        self.focus_time.setText(f"{hours}h {minutes}m")
        
        # Generate recommendation
        if self._state.cycles_today < 3:
            rec = "Keep going! You're building momentum 🚀"
        elif self._state.cycles_today < 6:
            rec = "Great pace! Consider a long break soon ☕"
        elif self._state.cycles_today == 6:
            rec = "Take a long break (15-30 min) 🌟"
        else:
            rec = "Excellent work! You've earned a rest! 🏆"
        
        self.recommendation_label.setText(rec)

    def _save_state(self) -> None:
        """Save state to state.json."""
        try:
            from app.state import load_state
            state = load_state()
            state.pomodoro_cycles = self._state
            save_state(state)
        except Exception as e:
            print(f"Error saving pomodoro cycles state: {e}")

    def get_state(self) -> PomodoroCyclesState:
        """Get current state."""
        return self._state

    def set_state(self, state: PomodoroCyclesState) -> None:
        """Set state from external source."""
        self._state = state
        self._update_display()
