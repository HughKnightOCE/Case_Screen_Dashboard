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

        # If a widget_order is provided in config, use it to build the vertical stack.
        # Otherwise fallback to explicit ordering of common widgets.
        order_to_use = order if order else [
            "focus_timer",
            "metrics",
            "focus_streak",
            "pomodoro_cycles",
            "university",
            "todo",
            "break_reminder",
            "hydration_reminder",
            "distraction_blocker",
            "logs",
        ]

        # Map friendly names used in config to actual widget keys
        key_map = {
            "pomodoro": "pomodoro_cycles",
            "pomodoro_cycles": "pomodoro_cycles",
        }

        for w in order_to_use:
            wt = key_map.get(w, w)
            widget = self._make_widget(cfg.get(wt, wt), wt)
            # sensible defaults for heights
            if wt == "focus_timer":
                widget.setMinimumHeight(320)
            elif wt == "metrics":
                widget.setMinimumHeight(240)
            elif wt in ("university", "todo"):
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
