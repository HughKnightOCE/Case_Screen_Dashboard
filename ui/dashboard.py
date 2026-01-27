from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout
from PySide6.QtCore import Qt

from app.config import DEFAULT_LAYOUT
from app.state import TodoItem
from ui.panels import LogsPanel
from ui.widgets import (
    FocusTimerWidget,
    MetricTile,
    TodoListWidget,
    UniTasksWidget,
    BreakReminderWidget,
    FocusStreakWidget,
    DistractionBlockerWidget,
    HydrationReminderWidget,
    PomodoroCyclesWidget,
)
from ui.widgets.fan_speed_widget import FanSpeedWidget
from ui.widgets.weather_widget import WeatherWidget
from ui.widgets.calendar_widget import CalendarWidget
from ui.widgets.habit_tracker_widget import HabitTrackerWidget
from ui.widgets.motivational_quote_widget import MotivationalQuoteWidget
from ui.widgets.system_stats_widget import SystemStatsWidget
from ui.widgets.countdown_widget import CountdownWidget
from ui.widgets.sticky_notes_widget import StickyNotesWidget
from ui.widgets.media_controls_widget import MediaControlsWidget
from ui.widgets.focus_music_widget import FocusMusicWidget
from ui.widgets.github_notifications_widget import GitHubNotificationsWidget


class DashboardView(QWidget):
    def __init__(self, layout_cfg: Optional[dict[str, str]] = None, widget_order: Optional[list[str]] = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        cfg = layout_cfg if isinstance(layout_cfg, dict) else dict(DEFAULT_LAYOUT)
        order = widget_order if isinstance(widget_order, list) else None

        # Widget handles
        self._metrics_tiles: dict[str, MetricTile] = {}
        self._logs_panel: Optional[LogsPanel] = None
        self._todo_widget: Optional[TodoListWidget] = None

        # Create scrollable area for better use of space
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("QWidget { background-color: #1e1e1e; }")
        
        # Main vertical layout - single column, full width
        main_vbox = QVBoxLayout(scroll_widget)
        main_vbox.setContentsMargins(40, 40, 40, 40)
        main_vbox.setSpacing(40)

        # Build layout from config dict (single-column slots: slot_1, slot_2, ..., slot_6)
        # Order slots by number: slot_1, slot_2, slot_3, slot_4, slot_5, slot_6
        slot_order = [f"slot_{i}" for i in range(1, 7)]
        
        for slot_name in slot_order:
            widget_type = cfg.get(slot_name, "blank")
            if widget_type == "blank":
                continue
            
            widget = self._make_widget(widget_type, widget_type)
            # sensible defaults for heights
            if widget_type == "focus_timer":
                widget.setMinimumHeight(320)
            elif widget_type == "metrics":
                widget.setMinimumHeight(240)
            elif widget_type in ("university", "todo"):
                widget.setMinimumHeight(300)
            else:
                widget.setMinimumHeight(200)
            main_vbox.addWidget(widget)
        
        # Add stretch at end to prevent widgets from being stretched
        main_vbox.addStretch(1)

        scroll.setWidget(scroll_widget)
        
        # Main layout for the view
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _make_widget(self, widget_type: str, fallback: str) -> QWidget:
        wt = widget_type if isinstance(widget_type, str) else fallback
        if wt == "blank":
            return QWidget(self)

        if wt == "university":
            return UniTasksWidget(self)

        if wt == "todo":
            self._todo_widget = TodoListWidget(self)
            return self._todo_widget

        if wt == "focus_timer":
            return FocusTimerWidget(self)

        if wt == "logs":
            self._logs_panel = LogsPanel("logs", self)
            return self._logs_panel

        if wt == "metrics":
            # Simple metrics block (three MetricTiles)
            box = QWidget(self)
            layout = QVBoxLayout(box)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)

            cpu = MetricTile("CPU LOAD", "0", "%", box)
            cpu.setMinimumHeight(70)
            gpu = MetricTile("GPU LOAD", "0", "%", box)
            gpu.setMinimumHeight(70)
            ram = MetricTile("RAM USED", "0.0", "GB", box)
            ram.setMinimumHeight(70)

            self._metrics_tiles = {"cpu": cpu, "gpu": gpu, "ram": ram}

            layout.addWidget(cpu)
            layout.addWidget(gpu)
            layout.addWidget(ram)

            box.setLayout(layout)
            return box

        # New ADHD/Focus widgets
        if wt == "break_reminder":
            return BreakReminderWidget(self)

        if wt == "focus_streak":
            return FocusStreakWidget(self)

        if wt == "distraction_blocker":
            return DistractionBlockerWidget(self)

        if wt == "hydration_reminder":
            return HydrationReminderWidget(self)

        if wt == "pomodoro_cycles":
            return PomodoroCyclesWidget(self)

        if wt == "fan_speed":
            return FanSpeedWidget(self)

        if wt == "weather":
            try:
                return WeatherWidget()
            except Exception:
                return QWidget(self)

        if wt == "calendar":
            try:
                return CalendarWidget()
            except Exception:
                return QWidget(self)

        if wt == "habit_tracker":
            try:
                return HabitTrackerWidget()
            except Exception:
                return QWidget(self)

        if wt == "motivational_quote":
            try:
                return MotivationalQuoteWidget()
            except Exception:
                return QWidget(self)

        if wt == "system_stats":
            try:
                return SystemStatsWidget()
            except Exception:
                return QWidget(self)

        if wt == "countdown":
            try:
                return CountdownWidget()
            except Exception:
                return QWidget(self)

        if wt == "sticky_notes":
            try:
                return StickyNotesWidget()
            except Exception:
                return QWidget(self)

        if wt == "media_controls":
            try:
                return MediaControlsWidget()
            except Exception:
                return QWidget(self)

        if wt == "focus_music":
            try:
                return FocusMusicWidget()
            except Exception:
                return QWidget(self)

        if wt == "github_notifications":
            try:
                return GitHubNotificationsWidget()
            except Exception:
                return QWidget(self)

        # Unknown type -> fallback
        if wt != fallback:
            return self._make_widget(fallback, fallback)
        return QWidget(self)

    # ---- hooks used by MainWindow heartbeat ----
    def set_metrics(self, cpu_temp: int, gpu_load: int, ram_used: float) -> None:
        if not self._metrics_tiles:
            return
        self._metrics_tiles["cpu"].set_value(str(cpu_temp))
        self._metrics_tiles["gpu"].set_value(str(gpu_load))
        self._metrics_tiles["ram"].set_value(f"{ram_used:.1f}")

    def append_log(self, line: str) -> None:
        if self._logs_panel is None:
            return
        self._logs_panel.append_line(line)

    def set_todos(self, todos: list[TodoItem]) -> None:
        if self._todo_widget is None:
            return
        self._todo_widget.set_items(todos)

    def get_todos(self) -> list[TodoItem]:
        if self._todo_widget is None:
            return []
        return self._todo_widget.get_items()
