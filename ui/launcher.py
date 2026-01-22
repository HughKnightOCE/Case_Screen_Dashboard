from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSpinBox,
)

from app.config import PRESETS


def list_screens() -> list[str]:
    """
    Returns a list of human-readable screen descriptions.
    Uses QGuiApplication directly (no app arg required).
    """
    screens = QGuiApplication.screens()
    result: list[str] = []

    for i, s in enumerate(screens):
        geo = s.geometry()
        result.append(
            f"[{i}] {s.name()} {geo.width()}x{geo.height()} @({geo.x()},{geo.y()})"
        )

    return result


class LaunchDialog(QDialog):
    """
    Standalone launcher dialog for dashboard configuration.
    
    Responsibilities:
    - Select target screen
    - Choose layout preset
    - Adjust font size
    - Manage university tasks
    - Manage todo tasks
    - Persist configuration and state
    """

    def __init__(self, cfg) -> None:
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle("Case Dashboard Launcher")
        self.setMinimumSize(700, 650)
        self.setMaximumSize(900, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === DISPLAY SECTION ===
        display_box = QGroupBox("Display Configuration")
        display_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        display_layout = QVBoxLayout(display_box)
        display_layout.setSpacing(8)
        display_layout.setContentsMargins(12, 16, 12, 12)
        
        display_label = QLabel("Select Display Screen:")
        display_label.setStyleSheet("font-size: 11pt;")
        self.screen_combo = QComboBox()
        self.screen_combo.addItems(list_screens())
        self.screen_combo.setStyleSheet("font-size: 11pt; padding: 4px;")
        if cfg.display_index >= 0:
            self.screen_combo.setCurrentIndex(cfg.display_index)
        self.screen_combo.setMinimumHeight(28)
        display_layout.addWidget(display_label)
        display_layout.addWidget(self.screen_combo)
        main_layout.addWidget(display_box)

        # === LAYOUT SECTION ===
        layout_box = QGroupBox("Dashboard Layout")
        layout_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        layout_layout = QVBoxLayout(layout_box)
        layout_layout.setSpacing(8)
        layout_layout.setContentsMargins(12, 16, 12, 12)
        
        layout_label = QLabel("Choose Layout Preset:")
        layout_label.setStyleSheet("font-size: 11pt;")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(list(PRESETS.keys()))
        self.layout_combo.setStyleSheet("font-size: 11pt; padding: 4px;")
        self.layout_combo.setCurrentText("productivity_2col")
        self.layout_combo.setMinimumHeight(28)
        layout_layout.addWidget(layout_label)
        layout_layout.addWidget(self.layout_combo)
        main_layout.addWidget(layout_box)

        # === FONT SIZE SECTION ===
        font_box = QGroupBox("Application Font Size")
        font_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        font_layout = QVBoxLayout(font_box)
        font_layout.setSpacing(8)
        font_layout.setContentsMargins(12, 16, 12, 12)
        
        font_label = QLabel("Font Size (points):")
        font_label.setStyleSheet("font-size: 11pt;")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setStyleSheet("font-size: 11pt; padding: 4px;")
        self.font_size_spin.setMinimum(12)
        self.font_size_spin.setMaximum(72)
        self.font_size_spin.setValue(48)
        self.font_size_spin.setSingleStep(2)
        self.font_size_spin.setMinimumHeight(28)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size_spin)
        main_layout.addWidget(font_box)

        # === UNIVERSITY TASKS SECTION ===
        uni_box = QGroupBox("University Tasks")
        uni_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        uni_layout = QVBoxLayout(uni_box)
        uni_layout.setContentsMargins(12, 16, 12, 12)
        
        uni_manage_btn = QPushButton("Manage University Tasks")
        uni_manage_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        uni_manage_btn.setMinimumHeight(32)
        uni_manage_btn.clicked.connect(self._open_uni_dialog)
        uni_layout.addWidget(uni_manage_btn)
        main_layout.addWidget(uni_box)

        # === TODO TASKS SECTION ===
        todo_box = QGroupBox("Todo Tasks")
        todo_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        todo_layout = QVBoxLayout(todo_box)
        todo_layout.setContentsMargins(12, 16, 12, 12)
        
        todo_manage_btn = QPushButton("Manage Todo Tasks")
        todo_manage_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        todo_manage_btn.setMinimumHeight(32)
        todo_manage_btn.clicked.connect(self._open_todo_dialog)
        todo_layout.addWidget(todo_manage_btn)
        main_layout.addWidget(todo_box)

        # === WIDGET ORDER SECTION ===
        order_box = QGroupBox("Widget Order")
        order_box.setStyleSheet("QGroupBox { font-size: 11pt; font-weight: bold; padding-top: 12px; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; top: -6px; left: 10px; padding: 0 3px; }")
        order_layout = QVBoxLayout(order_box)
        order_layout.setContentsMargins(12, 16, 12, 12)

        order_label = QLabel("Drag to reorder widgets (top -> bottom display order):")
        order_label.setStyleSheet("font-size: 11pt;")
        order_layout.addWidget(order_label)

        self.order_list = QListWidget()
        self.order_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.order_list.setDefaultDropAction(Qt.MoveAction)
        self.order_list.setStyleSheet("font-size: 11pt; padding: 4px;")
        order_layout.addWidget(self.order_list)

        # populate order list from cfg if present
        from app.config import WIDGET_TYPES
        preferred = getattr(self.cfg, "widget_order", None)
        items = preferred if isinstance(preferred, list) else [w for w in WIDGET_TYPES if w != "blank"]
        for it in items:
            li = QListWidgetItem(it)
            self.order_list.addItem(li)

        main_layout.addWidget(order_box)

        # Add stretch to push everything to top
        main_layout.addStretch(1)

        # === BUTTONS AT BOTTOM ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        cancel_btn = QPushButton("Cancel")
        launch_btn = QPushButton("Launch Dashboard")
        
        cancel_btn.setStyleSheet("font-size: 11pt; padding: 8px; font-weight: bold;")
        launch_btn.setStyleSheet("font-size: 11pt; padding: 8px; font-weight: bold;")
        cancel_btn.setMinimumHeight(36)
        launch_btn.setMinimumHeight(36)
        
        cancel_btn.clicked.connect(self.reject)
        launch_btn.clicked.connect(self._accept)
        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(launch_btn)
        main_layout.addLayout(btn_row)

    def _open_uni_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage University Tasks")
        dialog.setModal(True)
        dialog.setMinimumSize(850, 550)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("University Tasks")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Unit", "Task", "Due Date", "Done"])
        table.setColumnWidth(0, 120)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 100)
        table.setMinimumHeight(350)
        table.setStyleSheet("font-size: 11pt; QHeaderView::section { font-size: 11pt; padding: 4px; }")
        layout.addWidget(table)

        # Load existing
        uni_file = Path(__file__).resolve().parents[1] / "uni_tasks.json"
        try:
            data = json.loads(uni_file.read_text(encoding="utf-8"))
            for item in data:
                self._add_uni_row(table, item["unit"], item["task"], item["due"], item.get("done", False))
        except:
            pass

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        add_btn = QPushButton("+ Add Task")
        delete_btn = QPushButton("- Delete Selected")
        ok_btn = QPushButton("Done")
        add_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        delete_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        ok_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        add_btn.setMinimumHeight(32)
        delete_btn.setMinimumHeight(32)
        ok_btn.setMinimumHeight(32)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(lambda: self._add_uni_row(table, "", "", "", False))
        delete_btn.clicked.connect(lambda: self._delete_row(table))
        ok_btn.clicked.connect(dialog.accept)

        dialog.exec()

        # Save
        tasks = []
        for row in range(table.rowCount()):
            unit = table.item(row, 0).text().strip() if table.item(row, 0) else ""
            task = table.item(row, 1).text().strip() if table.item(row, 1) else ""
            due = table.item(row, 2).text().strip() if table.item(row, 2) else ""
            done = table.item(row, 3).checkState() == Qt.CheckState.Checked if table.item(row, 3) else False
            if unit or task:
                tasks.append({"unit": unit, "task": task, "due": due, "done": done})
        try:
            uni_file.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        except:
            pass

    def _open_todo_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Todo Tasks")
        dialog.setModal(True)
        dialog.setMinimumSize(750, 500)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Daily Todo Tasks")
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(title)

        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Task", "Done"])
        table.setColumnWidth(0, 600)
        table.setColumnWidth(1, 100)
        table.setMinimumHeight(350)
        table.setStyleSheet("font-size: 11pt; QHeaderView::section { font-size: 11pt; padding: 4px; }")
        layout.addWidget(table)

        # Load existing
        from app.state import load_state
        try:
            state = load_state()
            for todo in state.todos:
                self._add_todo_row(table, todo.text, todo.done)
        except:
            pass

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        add_btn = QPushButton("+ Add Task")
        delete_btn = QPushButton("- Delete Selected")
        ok_btn = QPushButton("Done")
        add_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        delete_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        ok_btn.setStyleSheet("font-size: 11pt; padding: 6px;")
        add_btn.setMinimumHeight(32)
        delete_btn.setMinimumHeight(32)
        ok_btn.setMinimumHeight(32)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        add_btn.clicked.connect(lambda: self._add_todo_row(table, "", False))
        delete_btn.clicked.connect(lambda: self._delete_row(table))
        ok_btn.clicked.connect(dialog.accept)

        dialog.exec()

        # Save
        from app.state import save_state, AppState, TodoItem
        todos = []
        for row in range(table.rowCount()):
            task = table.item(row, 0).text().strip() if table.item(row, 0) else ""
            done = table.item(row, 1).checkState() == Qt.CheckState.Checked if table.item(row, 1) else False
            if task:
                todos.append(TodoItem(text=task, done=done))
        try:
            state = AppState(todos=todos)
            save_state(state)
        except:
            pass

    def _add_uni_row(self, table: QTableWidget, unit: str, task: str, due: str, done: bool):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(unit))
        table.setItem(row, 1, QTableWidgetItem(task))
        table.setItem(row, 2, QTableWidgetItem(due))
        done_item = QTableWidgetItem("")
        done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        done_item.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked)
        table.setItem(row, 3, done_item)

    def _add_todo_row(self, table: QTableWidget, task: str, done: bool):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(task))
        done_item = QTableWidgetItem("")
        done_item.setFlags(done_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        done_item.setCheckState(Qt.CheckState.Checked if done else Qt.CheckState.Unchecked)
        table.setItem(row, 1, done_item)

    def _delete_row(self, table: QTableWidget):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    def _accept(self) -> None:
        """
        Persist selections into config object.
        """
        self.cfg.display_index = self.screen_combo.currentIndex()
        preset_name = self.layout_combo.currentText()
        self.cfg.layout = PRESETS.get(preset_name, PRESETS["productivity_2col"])
        self.cfg.font_size = self.font_size_spin.value()
        # Save widget order from list
        try:
            order = [self.order_list.item(i).text() for i in range(self.order_list.count())]
            self.cfg.widget_order = order
        except Exception:
            pass
        
        self.accept()

    def apply_to_config(self):
        return self.cfg
