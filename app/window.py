from __future__ import annotations

import time

from PySide6.QtCore import QTimer, QRect, Qt
from PySide6.QtGui import QCloseEvent, QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton

import psutil

from app.config import AppConfig
from app.state import load_state, save_state, AppState
from ui.dashboard import DashboardView


class MainWindow(QMainWindow):
    def __init__(self, screen_geometry: QRect, cfg: AppConfig) -> None:
        super().__init__()

        self.setWindowTitle("case dashboard")
        self.setGeometry(screen_geometry)

        # Create main container
        container = QWidget(self)
        self.setCentralWidget(container)

        # Create vertical layout for the container
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create top bar with quit button
        top_bar = QWidget(self)
        top_bar.setMaximumHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 8, 10, 8)
        top_bar_layout.setSpacing(0)
        top_bar_layout.addStretch()  # Push button to the right

        # Create quit button
        quit_button = QPushButton("✕", self)
        quit_button.setFixedSize(40, 40)
        quit_button.clicked.connect(self.close)
        quit_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #e6edf3;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.25);
            }
            """
        )
        top_bar_layout.addWidget(quit_button)
        top_bar.setLayout(top_bar_layout)

        # Add top bar and dashboard to main layout
        main_layout.addWidget(top_bar, 0)

        self.dashboard = DashboardView(layout_cfg=cfg.layout, widget_order=getattr(cfg, "widget_order", None), parent=container)
        main_layout.addWidget(self.dashboard, 1)

        container.setLayout(main_layout)

        # Create menu bar with Quit option (hidden but still functional)
        menu_bar = self.menuBar()
        menu_bar.hide()
        file_menu = menu_bar.addMenu("File")
        quit_action = QAction("Quit (Ctrl+Q)", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Load state
        state = load_state()
        self.dashboard.set_todos(state.todos)

        # ---- Heartbeat timer (placeholder metrics/logs) ----
        self._t0 = time.time()
        self._tick = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(1000)

    def _on_tick(self) -> None:
        self._tick += 1

        cpu_load = psutil.cpu_percent()
        gpu_load = cpu_load  # Placeholder: use CPU for GPU
        ram_used = round(psutil.virtual_memory().used / (1024**3), 1)

        self.dashboard.set_metrics(cpu_temp=cpu_load, gpu_load=gpu_load, ram_used=ram_used)

        if self._tick % 10 == 0:
            self.dashboard.append_log(
                f"[ui] tick={self._tick} cpu={cpu_load}% gpu={gpu_load}% ram={ram_used}gb"
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        # Save state on close
        todos = self.dashboard.get_todos()
        state = AppState(todos=todos)
        save_state(state)
        super().closeEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.close()
        super().keyPressEvent(event)
